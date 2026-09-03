-- =====================================================
-- MIGRAÇÃO: Trigger de Validação do Período da Leitura
-- =====================================================

-- VAL-04: Leitura dentro do período do cilindro
-- Impede que uma leitura seja registrada com data fora do período do cilindro
CREATE OR REPLACE FUNCTION validar_leitura_periodo()
RETURNS TRIGGER AS $$
DECLARE
  cil RECORD;
BEGIN
  IF NEW.cilindro_id IS NULL THEN
    RETURN NEW;
  END IF;

  SELECT data_inicio_consumo, data_fim INTO cil
  FROM public.cilindro WHERE id = NEW.cilindro_id;

  IF FOUND THEN
    IF cil.data_inicio_consumo IS NOT NULL AND NEW.data < cil.data_inicio_consumo THEN
      RAISE EXCEPTION 'Data da leitura (%) é anterior ao início do cilindro (%)',
        NEW.data, cil.data_inicio_consumo;
    END IF;

    IF cil.data_fim IS NOT NULL AND NEW.data > cil.data_fim THEN
      RAISE EXCEPTION 'Data da leitura (%) é posterior ao fim do cilindro (%)',
        NEW.data, cil.data_fim;
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- NOTA: Ativo no banco em 2026-09-03 após corrigir os dados (BUG-04),
-- quando as leituras fora do período foram zeradas (validação = 0).

CREATE TRIGGER trg_validar_leitura_periodo
BEFORE INSERT OR UPDATE ON public.leitura
FOR EACH ROW EXECUTE FUNCTION validar_leitura_periodo();
