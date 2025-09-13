-- Correction des unités sur Render
-- Date: 2025-09-13 13:29:01

-- 1. Changer le type de 1 1/2 à 4 1/2
UPDATE units SET type = '4 1/2' WHERE type = '1 1/2';

-- 2. Corriger les adresses doublées
-- Exemple: '56 56-58-60-62 rue Vachon' → '56 rue Vachon'
UPDATE units SET unit_address = 
  CASE 
    WHEN unit_address LIKE '% %' AND 
         SUBSTR(unit_address, INSTR(unit_address, ' ') + 1) LIKE '%-%' AND 
         SUBSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), 1, INSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), ' ') - 1) GLOB '*[0-9]*' 
    THEN SUBSTR(unit_address, 1, INSTR(unit_address, ' ') - 1) || ' ' || 
         SUBSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), INSTR(SUBSTR(unit_address, INSTR(unit_address, ' ') + 1), ' ') + 1)
    ELSE unit_address
  END
WHERE unit_address LIKE '% %' AND 
      SUBSTR(unit_address, INSTR(unit_address, ' ') + 1) LIKE '%-%';

-- 3. Vérifier le résultat
SELECT id, unit_number, type, unit_address FROM units;