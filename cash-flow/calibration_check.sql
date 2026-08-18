-- Cash-flow månadskalibrering — underlag för genomgången med CEO vid månadsstängning.
-- Körs: ssh ... "dbshell" < calibration_check.sql   (eller klistra in blocken)
-- Syfte: hitta MÅNADSTOTALER som glidit från bokföringen. Inte per-transaktionsmatchning.

\echo '=== 1. MODELL vs BOKFÖRING (kr/mån per konto) — glidning i kalibrering'
WITH model AS (
  SELECT account_number,
         SUM(CASE frequency
               WHEN 'monthly'   THEN amount
               WHEN 'quarterly' THEN amount/3
               WHEN 'annual'    THEN amount/12
             END) AS model_mo
  FROM recurring_payment
  WHERE enabled AND NOT is_internal_transfer
    AND currency = 'SEK' AND account_number IS NOT NULL
  GROUP BY account_number
), sie AS (
  SELECT account_number,
         AVG(amount) FILTER (WHERE period >= to_char(CURRENT_DATE - interval '12 months','YYYYMM')) AS sie_12m,
         AVG(amount) FILTER (WHERE period >= to_char(CURRENT_DATE - interval '4 months','YYYYMM'))  AS sie_3m
  FROM sie_monthly_balances
  WHERE account_number ~ '^[4-7]'
  GROUP BY account_number
)
SELECT m.account_number AS konto,
       ROUND(m.model_mo)        AS modell,
       ROUND(m.model_mo/1.25)   AS modell_exkl_moms,
       ROUND(s.sie_3m)          AS bokf_3m,
       ROUND(s.sie_12m)         AS bokf_12m,
       ROUND(m.model_mo/1.25 - s.sie_12m) AS avvik_exkl,
       ROUND(m.model_mo         - s.sie_12m) AS avvik_inkl
FROM model m JOIN sie s USING (account_number)
-- OR, inte AND: konton med omvand skattskyldighet (OpenRouter, AWS, Voxbone...) bar INGEN svensk moms,
-- sa for dem ar RAkolumnen ratt jamforelse. Ett AND-villkor dolde att 6540 var overmodellerat 27-40K/man
-- (upptackt 2026-08-17). Fler falska positiva ar priset - agenten tillampar momsregeln vid genomgangen.
WHERE ABS(m.model_mo/1.25 - s.sie_12m) > 10000
   OR ABS(m.model_mo      - s.sie_12m) > 10000
ORDER BY GREATEST(ABS(m.model_mo/1.25 - s.sie_12m), 0) DESC;

\echo ''
\echo '=== 2. KOSTNADSKONTON UTAN PROGNOSRAD — helt omodellerat (som DBT Lån 2 var)'
SELECT s.account_number AS konto,
       ROUND(AVG(s.amount)) AS bokf_12m_snitt,
       ROUND(SUM(s.amount)) AS bokf_12m_totalt
FROM sie_monthly_balances s
WHERE s.account_number ~ '^[4-7]'
  AND s.period >= to_char(CURRENT_DATE - interval '12 months','YYYYMM')
  AND s.account_number NOT IN (SELECT account_number FROM recurring_payment WHERE enabled AND account_number IS NOT NULL)
  -- Medvetet omodellerade konton (skäl i SKILL.md). Uppdatera listan när ett skäl upphör.
  AND s.account_number NOT IN (
    '7811','7812','7814','7960','3960','7290',  -- avskrivningar, FX, semesterlöneskuld: icke-kassaflöde
    '4531','4535','4540',                        -- omvänd skattskyldighet, bokföringsplumbing som nettar ut
    '4018','4014','4013','4017','4019','4020','4021','4030',  -- COGS via cogs_factor / betalas ur PayPal
    '5991','5992','5800',                        -- ligger inne i SEB Kort id 7
    '7210','7240'                                -- ligger inne i löner id 12 resp styrelsearvode id 32/33
  )
GROUP BY s.account_number
HAVING AVG(s.amount) > 10000
ORDER BY AVG(s.amount) DESC;

\echo ''
\echo '=== 3. BALANSKONTON — vad vi är skyldiga vs vad som ligger inplanerat'
WITH bal AS (
  SELECT account_number, period,
         SUM(amount) OVER (PARTITION BY account_number ORDER BY period) AS saldo,
         ROW_NUMBER() OVER (PARTITION BY account_number ORDER BY period DESC) rn
  FROM sie_monthly_balances
  -- OBS: bara konton där den löpande summan FAKTISKT är saldot. 2852 exkluderat: dess rader
  -- är anståndsBETALNINGAR (debet), inte skulden - summan blir kumulativa betalningar, inte kvarvarande skuld.
  WHERE account_number IN ('2890','2820','2899','1650')
), sched AS (
  SELECT account_number, SUM(amount) AS planerat
  FROM scheduled_payment
  WHERE enabled AND NOT is_inflow AND pay_date >= CURRENT_DATE
  GROUP BY account_number
)
SELECT b.account_number AS konto, b.period AS senaste_sie,
       ROUND(b.saldo) AS bokfort_saldo,
       ROUND(COALESCE(s.planerat,0)) AS planerat_framat,
       ROUND(ABS(b.saldo) - COALESCE(s.planerat,0)) AS oplanerat
FROM bal b LEFT JOIN sched s USING (account_number)
WHERE b.rn = 1 AND ABS(b.saldo) > 50000
ORDER BY ABS(b.saldo) DESC;

\echo ''
\echo '=== 4. PROVISORISKA / PLACEHOLDER-RADER — med ålder. Inget får bäras tyst.'
SELECT 'sched' AS tabell, id, pay_date, left(recipient,45) AS mottagare, amount, currency,
       (CURRENT_DATE - created_at::date) AS dagar_gammal
FROM scheduled_payment
WHERE enabled AND (description ILIKE '%provisional%' OR description ILIKE '%placeholder%'
                   OR description ILIKE '%provisor%' OR recipient ILIKE '%provisional%')
UNION ALL
SELECT 'recur', id, NULL, left(recipient,45), amount, currency, (CURRENT_DATE - created_at::date)
FROM recurring_payment
WHERE enabled AND (description ILIKE '%provisional%' OR description ILIKE '%placeholder%'
                   OR description ILIKE '%provisor%')
ORDER BY dagar_gammal DESC;

\echo ''
\echo '=== 5. INTÄKTSÖVERSTYRNING — mandatorisk genomgång varje session'
SELECT parameter_name, parameter_value, updated_at,
       (CURRENT_DATE - updated_at::date) AS dagar_sedan_satt
FROM business_parameters
WHERE parameter_name IN ('cashflow_revenue_override_msek','cashflow_cogs_percent');

\echo ''
\echo '=== 6. RADER UTAN ANDRINGSLOGG eller utan beloppsandring pa 12 man (CR-2026-08-17)'
SELECT r.id, left(r.recipient,38) AS rad, r.amount,
       COALESCE(to_char(max(h.changed_at)::date,'YYYY-MM-DD'),'ALDRIG LOGGAD') AS senaste_loggpost,
       count(h.*) FILTER (WHERE 'amount' = ANY(h.changed_fields)) AS beloppsandringar
FROM recurring_payment r
LEFT JOIN forecast_change_log h
       ON h.table_name='recurring_payment' AND h.row_id=r.id
WHERE r.enabled
GROUP BY r.id, r.recipient, r.amount
HAVING max(h.changed_at) IS NULL
    OR max(h.changed_at) < CURRENT_DATE - interval '12 months'
ORDER BY r.amount DESC;
