-- ============================================================================
-- TABELA: badges_desbloqueados
-- DESCRIÇÃO: Registro de todas as conquistas/badges desbloqueadas pelos analistas
-- DATA: 13/11/2025
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.badges_desbloqueados (
    id SERIAL PRIMARY KEY,
    user_type VARCHAR(10) NOT NULL, -- 'EV', 'SDR', 'LDR'
    user_id VARCHAR(50) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    badge_code VARCHAR(50) NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    badge_category VARCHAR(50) NOT NULL, -- 'volume', 'valor', 'horario', 'velocidade'
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deal_id VARCHAR(50),
    deal_name VARCHAR(255),
    metric_value DECIMAL(15,2), -- Valor do deal ou quantidade
    pipeline VARCHAR(50), -- Para SDRs: 'NEW' ou 'Expansão'
    source VARCHAR(20) DEFAULT 'hubspot_api', -- Fonte dos dados
    context JSONB -- Dados adicionais em JSON
);

-- Índice único para evitar duplicatas por dia
CREATE UNIQUE INDEX IF NOT EXISTS idx_badges_unique_per_day 
ON public.badges_desbloqueados(user_type, user_id, badge_code, DATE(unlocked_at));

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_badges_user ON public.badges_desbloqueados(user_type, user_id);
CREATE INDEX IF NOT EXISTS idx_badges_date ON public.badges_desbloqueados(unlocked_at DESC);
CREATE INDEX IF NOT EXISTS idx_badges_category ON public.badges_desbloqueados(badge_category);
CREATE INDEX IF NOT EXISTS idx_badges_code ON public.badges_desbloqueados(badge_code);

-- Comentários
COMMENT ON TABLE public.badges_desbloqueados IS 'Registro de badges/conquistas desbloqueadas na Black November 2025';
COMMENT ON COLUMN public.badges_desbloqueados.user_type IS 'Tipo de usuário: EV (Executivo de Vendas), SDR (Sales Development Rep), LDR (Lead Development Rep)';
COMMENT ON COLUMN public.badges_desbloqueados.badge_code IS 'Código único do badge: godlike, hat_trick, speed_demon, etc';
COMMENT ON COLUMN public.badges_desbloqueados.badge_category IS 'Categoria: volume, valor, horario, velocidade';
COMMENT ON COLUMN public.badges_desbloqueados.pipeline IS 'Para SDRs: NEW (pipeline 6810518) ou Expansão (pipeline 4007305)';
COMMENT ON COLUMN public.badges_desbloqueados.context IS 'Dados adicionais em JSON (timestamps, deals relacionados, etc)';
