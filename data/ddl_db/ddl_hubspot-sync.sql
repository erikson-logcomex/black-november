-- DROP SCHEMA public;

CREATE SCHEMA public AUTHORIZATION pg_database_owner;

COMMENT ON SCHEMA public IS 'standard public schema';

-- DROP TYPE public.halfvec;

CREATE TYPE public.halfvec (
	INPUT = halfvec_in,
	OUTPUT = halfvec_out,
	RECEIVE = halfvec_recv,
	SEND = halfvec_send,
	TYPMOD_IN = halfvec_typmod_in,
	ALIGNMENT = 4,
	STORAGE = secondary,
	CATEGORY = U,
	DELIMITER = ',');

-- DROP TYPE public.sparsevec;

CREATE TYPE public.sparsevec (
	INPUT = sparsevec_in,
	OUTPUT = sparsevec_out,
	RECEIVE = sparsevec_recv,
	SEND = sparsevec_send,
	TYPMOD_IN = sparsevec_typmod_in,
	ALIGNMENT = 4,
	STORAGE = secondary,
	CATEGORY = U,
	DELIMITER = ',');

-- DROP TYPE public.vector;

CREATE TYPE public.vector (
	INPUT = vector_in,
	OUTPUT = vector_out,
	RECEIVE = vector_recv,
	SEND = vector_send,
	TYPMOD_IN = vector_typmod_in,
	ALIGNMENT = 4,
	STORAGE = secondary,
	CATEGORY = U,
	DELIMITER = ',');

-- DROP SEQUENCE public.badges_desbloqueados_id_seq;

CREATE SEQUENCE public.badges_desbloqueados_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.hubspot_properties_id_seq;

CREATE SEQUENCE public.hubspot_properties_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.sync_status_id_seq;

CREATE SEQUENCE public.sync_status_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;-- public.activities definição

-- Drop table

-- DROP TABLE public.activities;

CREATE TABLE public.activities (
	"Record ID" int8 NULL,
	"Atividade atribuída a" varchar(50) NULL,
	"Duração da chamada" varchar(50) NULL,
	"Resultado da chamada" varchar(50) NULL,
	"Tipo de chamada e reunião" varchar(50) NULL,
	"Data_da_atividade" varchar(50) NULL,
	"Equipe da HubSpot" varchar(50) NULL,
	"Tipo de atividade" varchar(50) NULL
);


-- public.association_company_contact definição

-- Drop table

-- DROP TABLE public.association_company_contact;

CREATE TABLE public.association_company_contact (
	company_id int8 NOT NULL,
	contact_id int8 NOT NULL,
	"label" text NULL,
	row_updatedat timestamp DEFAULT now() NULL,
	CONSTRAINT association_company_contact_pkey UNIQUE (company_id, contact_id)
);


-- public.association_company_deal definição

-- Drop table

-- DROP TABLE public.association_company_deal;

CREATE TABLE public.association_company_deal (
	company_id int8 NOT NULL,
	deal_id int8 NOT NULL,
	row_updatedat timestamp DEFAULT now() NOT NULL,
	"label" text NULL,
	CONSTRAINT association_company_deal_pkey UNIQUE (company_id, deal_id)
);


-- public.badges_desbloqueados definição

-- Drop table

-- DROP TABLE public.badges_desbloqueados;

CREATE TABLE public.badges_desbloqueados (
	id serial4 NOT NULL,
	user_type varchar(10) NOT NULL, -- Tipo de usuário: EV (Executivo de Vendas), SDR (Sales Development Rep), LDR (Lead Development Rep)
	user_id varchar(50) NOT NULL,
	user_name varchar(255) NOT NULL,
	badge_code varchar(50) NOT NULL, -- Código único do badge: godlike, hat_trick, speed_demon, etc
	badge_name varchar(100) NOT NULL,
	badge_category varchar(50) NOT NULL, -- Categoria: volume, valor, horario, velocidade
	unlocked_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	deal_id varchar(50) NULL,
	deal_name varchar(255) NULL,
	metric_value numeric(15, 2) NULL,
	pipeline varchar(50) NULL, -- Para SDRs: NEW (pipeline 6810518) ou Expansão (pipeline 4007305)
	"source" varchar(20) DEFAULT 'hubspot_api'::character varying NULL,
	context jsonb NULL, -- Dados adicionais em JSON (timestamps, deals relacionados, etc)
	CONSTRAINT badges_desbloqueados_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_badges_category ON public.badges_desbloqueados USING btree (badge_category);
CREATE INDEX idx_badges_code ON public.badges_desbloqueados USING btree (badge_code);
CREATE INDEX idx_badges_date ON public.badges_desbloqueados USING btree (unlocked_at DESC);
CREATE UNIQUE INDEX idx_badges_unique_per_day ON public.badges_desbloqueados USING btree (user_type, user_id, badge_code, date(unlocked_at));
CREATE INDEX idx_badges_user ON public.badges_desbloqueados USING btree (user_type, user_id);
COMMENT ON TABLE public.badges_desbloqueados IS 'Registro de badges/conquistas desbloqueadas na Black November 2025';

-- Column comments

COMMENT ON COLUMN public.badges_desbloqueados.user_type IS 'Tipo de usuário: EV (Executivo de Vendas), SDR (Sales Development Rep), LDR (Lead Development Rep)';
COMMENT ON COLUMN public.badges_desbloqueados.badge_code IS 'Código único do badge: godlike, hat_trick, speed_demon, etc';
COMMENT ON COLUMN public.badges_desbloqueados.badge_category IS 'Categoria: volume, valor, horario, velocidade';
COMMENT ON COLUMN public.badges_desbloqueados.pipeline IS 'Para SDRs: NEW (pipeline 6810518) ou Expansão (pipeline 4007305)';
COMMENT ON COLUMN public.badges_desbloqueados.context IS 'Dados adicionais em JSON (timestamps, deals relacionados, etc)';


-- public.calls definição

-- Drop table

-- DROP TABLE public.calls;

CREATE TABLE public.calls (
	hs_object_id text NOT NULL,
	hubspot_owner_id text NULL,
	hs_created_by text NULL,
	hs_timestamp timestamptz NULL,
	hs_lastmodifieddate timestamptz NULL,
	hs_call_duration int4 NULL,
	hs_call_from_number varchar(50) NULL,
	hs_call_to_number varchar(50) NULL,
	hs_call_body text NULL,
	hs_call_disposition varchar(100) NULL,
	hs_activity_type varchar(50) NULL,
	hs_call_status varchar(50) NULL,
	hs_call_recording_url text NULL,
	hs_object_source_detail_1 text NULL,
	hs_call_direction varchar(20) NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	sync_status varchar(50) DEFAULT 'active'::character varying NULL,
	hubspot_raw_data jsonb NULL,
	CONSTRAINT calls_pkey PRIMARY KEY (hs_object_id)
);


-- public.companies definição

-- Drop table

-- DROP TABLE public.companies;

CREATE TABLE public.companies (
	hs_object_id int8 NOT NULL,
	"name" text NULL,
	"domain" text NULL,
	cnpj text NULL,
	createdate timestamp NULL,
	hs_lastmodifieddate timestamp NULL,
	notes_last_updated timestamp NULL,
	data_do_ultimo_periodo date NULL,
	segmento_1 text NULL,
	segmento_2 text NULL,
	segmento_3 text NULL,
	country text NULL,
	phone text NULL,
	lifecyclestage text NULL,
	status_da_empresa text NULL,
	faturamento_anual_ic text NULL,
	cnpj_situacao_cadastral_ic text NULL,
	cnae_id text NULL,
	cnae text NULL,
	score_de_credito_categoria text NULL,
	score_de_credito_detalhes text NULL,
	score_de_credito_ultima_atualizacao timestamptz NULL,
	fob_anual_ic text NULL,
	num_associated_contacts int4 NULL,
	num_associated_deals int4 NULL,
	hs_num_open_deals int4 NULL,
	address text NULL,
	address2 text NULL,
	am_data_de_solicitacao timestamp NULL,
	aut_customer_health_status_cs text NULL,
	aut_ob_flag_acionada_cs text NULL,
	bu_cliente text NULL,
	bu_guardiao_secundario text NULL,
	jur_aviso_previo_cancelamento text NULL,
	city text NULL,
	classificacao_cs text NULL,
	classificacao_mrr_bu_is text NULL,
	classificacao_mrr_bu_os text NULL,
	cliente_automacao text NULL,
	closed_won_reason_cs text NULL,
	cnpj_gerador_de_leads text NULL,
	codigo_hs text NULL,
	contrato_valor_total_recorrente numeric(18, 2) NULL,
	cs_abrir_card_no_hubspot_cs text NULL,
	cs_cumprindo_aviso_previo_clonado text NULL,
	cs_data_do_ultimo_risco_mapeado timestamp NULL,
	cs_emissao_de_nf_clonado text NULL,
	cs_etapa_no_pipeline_de_risco text NULL,
	cs_exp_cargo_do_solicitante text NULL,
	cs_exp_contato_solicitante text NULL,
	cs_exp_detalhes_da_oportunidade text NULL,
	cs_exp_origem_nova_receita text NULL,
	cs_exp_prioridade_de_contato text NULL,
	cs_inadimplencia_qtd_de_notas int4 NULL,
	cs_origem_da_perda text NULL,
	cs_possui_negocio_aberto_em_perda text NULL,
	cs_potencial_expansao text NULL,
	cs_segmentacao_cs text NULL,
	cs_suporte_premium text NULL,
	cs_tickets_nos_ultimos_30_dias int4 NULL,
	data_do_ultimo_perdido timestamp NULL,
	duracao_da_implementacao text NULL,
	empresa_de_grupo_economico text NULL,
	empresa_estrangeira text NULL,
	etapa_em_perda text NULL,
	ev_maturidade_do_cliente text NULL,
	faturamento_anual_em_dolares_usd text NULL,
	faturamento_dividido text NULL,
	fin_data_de_pagamento_clonado timestamp NULL,
	fin_faturamento_padrao_clonado text NULL,
	fin_forma_de_pagamento_clonado text NULL,
	fin_tem_pedido_de_compra text NULL,
	fin_tipo_de_faturamento_clonado text NULL,
	fin_vencimento_nf text NULL,
	health_score_acessos numeric(18, 2) NULL,
	health_score_ces numeric(18, 2) NULL,
	health_score_crescimento_cliente numeric(18, 2) NULL,
	health_score_inadimplencia numeric(18, 2) NULL,
	health_score_interacao_cliente numeric(18, 2) NULL,
	health_score_nota numeric(18, 2) NULL,
	health_score_nps numeric(18, 2) NULL,
	health_score_sem_sentimento numeric(18, 2) NULL,
	health_score_sentimento numeric(18, 2) NULL,
	health_score_tickets_outros numeric(18, 2) NULL,
	health_score_tickets_problema numeric(18, 2) NULL,
	health_score_usa_logmanager numeric(18, 2) NULL,
	health_score_usa_logtracking numeric(18, 2) NULL,
	health_score_usa_ncm numeric(18, 2) NULL,
	health_score_usa_shipment numeric(18, 2) NULL,
	health_score_usabilidade_geral numeric(18, 2) NULL,
	hs_country_code text NULL,
	hs_updated_by_user_id int8 NULL,
	hubspot_owner_assigneddate timestamp NULL,
	hubspot_owner_id text NULL,
	hubspot_team_id text NULL,
	id_lead text NULL,
	id_logcomex text NULL,
	idioma_do_cliente text NULL,
	implementador text NULL,
	implementador_cross_sell text NULL,
	jur_forma_de_renovacao text NULL,
	jur_reajuste_anual text NULL,
	jur_rescisao_antecipada_com_multa text NULL,
	jur_vigencia_do_contrato text NULL,
	mat_area_preparada_para_dado text NULL,
	mat_especializacao_em_comex text NULL,
	mat_nivel_utilizacao_de_dado text NULL,
	mkt_cliente_ativo text NULL,
	mkt_cliente_internacional text NULL,
	mkt_cnpj text NULL,
	mkt_nome_da_empresa text NULL,
	mkt_produtos_ativos text NULL,
	mrr_bu_intelligence numeric(18, 2) NULL,
	mrr_bu_operational numeric(18, 2) NULL,
	mrr_r numeric(18, 2) NULL,
	numberofemployees int4 NULL,
	ob_aud_auditoria_cliente_e_contrato text NULL,
	ob_aud_auditoria_engajamento_do_cliente text NULL,
	ob_aud_auditoria_insatisfacoes_e_problemas_clonado text NULL,
	ob_aud_auditoria_maturidade_do_cliente text NULL,
	ob_aud_auditoria_observacao_red_flags text NULL,
	ob_aud_auditoria_observacao_yellow_flags text NULL,
	ob_aud_observacoes_yellow_flag_in text NULL,
	ob_aud_yellow_flags_in_clonado text NULL,
	ob_aud_yellow_flags_out_clonado text NULL,
	ob_casos_de_uso text NULL,
	ob_data_de_agendamento_clonado timestamp NULL,
	ob_data_de_kickoff timestamp NULL,
	ob_i_classificacao_do_cliente text NULL,
	ob_i_cliente_liberado_sem_pgto text NULL,
	ob_i_conclusao_da_implementacao timestamp NULL,
	ob_i_frequencia_de_usabilidade text NULL,
	ob_i_inicio_da_implementacao timestamp NULL,
	ob_i_status_do_onboarding text NULL,
	ob_maturidade_do_cliente text NULL,
	ob_mostrou_risco_de_cancelar text NULL,
	ob_observacoes_red_flag_cs text NULL,
	ob_qtde_de_usuarios int4 NULL,
	ob_tipo_de_onboarding text NULL,
	obj_a_log_atende_o_objetivo_cs text NULL,
	obj_a_log_esta_contribuindo_cs text NULL,
	obj_estrategia_para_objetivo_cs text NULL,
	obj_nivel_de_atingimento_cs text NULL,
	obj_objetivo_com_o_produto_cs text NULL,
	obj_satisfacao_atingimento_cs text NULL,
	obj_tem_clareza_no_objetivo text NULL,
	og_aut_maturidade_do_cliente text NULL,
	og_cliente_sinalizou_perda text NULL,
	og_equipe_secundaria text NULL,
	og_reversao_de_perda text NULL,
	og_status_da_aprovacao_desconto_isencao_clonado text NULL,
	og_valor_revertido numeric(18, 2) NULL,
	ops_client_success text NULL,
	origem_da_empresa text NULL,
	pais_de_operacao_principal text NULL,
	pais_menu_suspenso text NULL,
	passagem_de_bastao_para_cs text NULL,
	quantidade_de_exportadores int4 NULL,
	sales_alteracao_no_plano_padrao text NULL,
	sales_isencao_de_pagamento_carencia text NULL,
	sales_percentual_de_desconto_no_mrr text NULL,
	sales_percentual_desconto_onboarding text NULL,
	sales_recuperacao_judicial text NULL,
	sales_venda_para_cpf text NULL,
	score_empresa_inadimplente text NULL,
	sdr_maturidade_do_cliente text NULL,
	state text NULL,
	sv_acoes_para_reversao text NULL,
	tipo_de_pagamento_frequencia text NULL,
	user_guardiao text NULL,
	user_guardiao_secundario text NULL,
	user_quality text NULL,
	valor_cif numeric(18, 2) NULL,
	website text NULL,
	zip text NULL,
	CONSTRAINT companies_pkey PRIMARY KEY (hs_object_id)
);


-- public.contacts definição

-- Drop table

-- DROP TABLE public.contacts;

CREATE TABLE public.contacts (
	hs_object_id text NOT NULL,
	firstname text NULL,
	lastname text NULL,
	email text NULL,
	full_name text NULL,
	jobtitle text NULL,
	phone text NULL,
	mobilephone text NULL,
	govcs_i_phone_number text NULL,
	city text NULL,
	country text NULL,
	createdate timestamp NULL,
	lastmodifieddate timestamp NULL,
	hubspot_owner_id text NULL,
	cargo_ text NULL,
	departamento text NULL,
	classificacao_ravena text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	sync_status text DEFAULT 'active'::character varying NULL,
	hubspot_raw_data jsonb NULL,
	tipo_de_contato text NULL,
	link_do_linkedin text NULL,
	guardiao__cs_ text NULL,
	cs__contatou_novo_contato_ text NULL,
	canal_de_aquisicao_do_contato text NULL,
	sales__feedback_do_contat text NULL,
	hs_whatsapp_phone_number text NULL,
	cs_suporte_premium text NULL,
	notes_last_contacted timestamp NULL,
	CONSTRAINT contacts_pkey PRIMARY KEY (hs_object_id),
	CONSTRAINT contacts_sync_status_check CHECK ((sync_status = ANY (ARRAY[('active'::character varying)::text, ('inactive'::character varying)::text, ('error'::character varying)::text, ('syncing'::character varying)::text])))
);
CREATE INDEX idx_contacts_createdate ON public.contacts USING btree (createdate);
CREATE INDEX idx_contacts_email ON public.contacts USING btree (email) WHERE (email IS NOT NULL);
CREATE INDEX idx_contacts_govcs_phone ON public.contacts USING btree (govcs_i_phone_number) WHERE (govcs_i_phone_number IS NOT NULL);
CREATE INDEX idx_contacts_lastmodified ON public.contacts USING btree (lastmodifieddate);
CREATE INDEX idx_contacts_phone ON public.contacts USING btree (phone) WHERE (phone IS NOT NULL);
CREATE INDEX idx_contacts_sync ON public.contacts USING btree (lastmodifieddate, sync_status);

-- Table Triggers

create trigger trg_update_contact_updated_at before
update
    on
    public.contacts for each row execute function update_contact_updated_at();


-- public.deal_notifications definição

-- Drop table

-- DROP TABLE public.deal_notifications;

CREATE TABLE public.deal_notifications (
	id text NOT NULL,
	deal_name text NULL,
	amount numeric NULL,
	owner_name text NULL,
	sdr_name text NULL,
	ldr_name text NULL,
	company_name text NULL,
	pipeline text NULL,
	deal_stage text NULL,
	payload jsonb NULL,
	created_at timestamptz DEFAULT now() NULL,
	viewed_by _text DEFAULT ARRAY[]::text[] NULL,
	CONSTRAINT deal_notifications_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_deal_notifications_created_at ON public.deal_notifications USING btree (created_at DESC);
CREATE INDEX idx_deal_notifications_viewed_by ON public.deal_notifications USING gin (viewed_by);


-- public.deal_stages_pipelines definição

-- Drop table

-- DROP TABLE public.deal_stages_pipelines;

CREATE TABLE public.deal_stages_pipelines (
	stage_id int8 NOT NULL,
	stage_label text NULL,
	stage_displayorder int4 NULL,
	stage_createdat timestamp NULL,
	stage_updatedat timestamp NULL,
	stage_active bool NULL,
	deal_isclosed bool NULL,
	pipeline_label text NULL,
	pipeline_active bool NULL,
	pipeline_displayorder int4 NULL,
	pipeline_id int8 NULL,
	pipeline_createdat timestamp NULL,
	pipeline_updatedat timestamp NULL,
	row_updatedat timestamp NULL,
	CONSTRAINT hubspot_deal_stages_pkey PRIMARY KEY (stage_id)
);


-- public.deals definição

-- Drop table

-- DROP TABLE public.deals;

CREATE TABLE public.deals (
	hs_object_id text NOT NULL,
	dealname text NULL,
	pipeline text NULL,
	dealstage text NULL,
	tipo_de_receita text NULL,
	empresa_internacional text NULL,
	tipo_de_negociacao text NULL,
	produto_principal text NULL,
	ramo_de_atuacao_do_negocio text NULL,
	amount_in_home_currency numeric(18, 2) NULL,
	valor_de_implementacao_us numeric(18, 2) NULL,
	valor_ganho numeric(18, 2) NULL,
	valor_de_implementacao numeric(18, 2) NULL,
	canal_de_aquisicao text NULL,
	hubspot_owner_id text NULL,
	criado_por text NULL,
	pr_vendedor text NULL,
	analista_comercial text NULL,
	user_account_manager text NULL,
	createdate timestamp NULL,
	data_de_entrada_na_etapa_distribuicao_vendas_nmrr timestamp NULL,
	data_de_prospect timestamp NULL,
	etapa_data_de_tentando_contato timestamp NULL,
	data_de_qualificacao timestamp NULL,
	data_de_agendamento timestamp NULL,
	fase_data_de_no_show timestamp NULL,
	data_de_demonstracao timestamp NULL,
	data_de_onboarding_trial timestamp NULL,
	data_de_proposta timestamp NULL,
	etapa_data_de_entrada_em_fechamento timestamp NULL,
	sales_data_de_faturamento timestamp NULL,
	closedate timestamp NULL,
	notes_next_activity_date timestamp NULL,
	data_prevista_reuniao timestamp NULL,
	notes_last_updated timestamp NULL,
	hs_lastmodifieddate timestamp NULL,
	faturamento_anual_ic text NULL,
	fob_anual_ic text NULL,
	sales_sal_sales_accepted_lead text NULL,
	status_de_agendamento text NULL,
	ultima_etapa_antes_do_perdido text NULL,
	ops_id_negocio_de_origem text NULL,
	presales_temperatura_v2 text NULL,
	temperatura_do_deal text NULL,
	macro_segmento_oficial text NULL,
	etapa_data_do_reagendamento text NULL,
	deal_cycle text NULL,
	coordenador text NULL,
	motivo_de_perda_n1 text NULL,
	campanha text NULL,
	fin_erro_de_dados_para_faturamento text NULL,
	tag_ops text NULL,
	closed_lost_reason text NULL,
	motivo_de_perda_n2 text NULL,
	sales_a_empresa_estava_no_timing_para_uma_contratacao text NULL,
	sales_a_reuniao_foi_realizada_com_uma_persona_adequada text NULL,
	sales_a_qualificacao_snippet_esta_preenchida_e_de_forma_clara text NULL,
	sales_a_dor_mapeada_pelo_pre_vendedor text NULL,
	score_de_credito_categoria text NULL,
	sales_percentual_de_desconto_clonado text NULL,
	sales_tem_uma_pessoa_ou_time_dedicado_para_analise_de_dados text NULL,
	sales_usa_dados_para_as_tomadas_de_decisoes_na_empresa text NULL,
	closed_won_reason text NULL,
	produto_intencao text NULL,
	produto_do_agendamento text NULL,
	sales_produtos_apresentados_na_demo text NULL,
	bu_business_unit text NULL,
	sales_business_unit text NULL,
	sales_business_unit_de_intencao text NULL,
	sales_business_unit_do_agendamento text NULL,
	sales_business_unit_da_demonstracao text NULL,
	sales_quais_as_principais_dores_e_impacto_de_nao_resolver text NULL,
	como_esse_lead_foi_aquecido_para_chegar_no_agendamento_primeiro text NULL,
	sales_principal_meio_de_comunicacao_utilizado_para_realizar_o_a text NULL,
	o_decisor_participou_da_reuniao text NULL,
	sales_de_chance_de_fechamento text NULL,
	sales_feedback_do_produto text NULL,
	sales_quando_pretende_ter_essa_dor_resolvida text NULL,
	amount numeric(18, 2) NULL,
	sales_budget_existe_orcamento_mapeado_para_sanar_essa_dor text NULL,
	sales_processo_de_adesao_proximos_passos_pessoas_a_serem_envolv text NULL,
	sales_proximos_passos text NULL,
	motivo_de_ganho text NULL,
	"json" jsonb NULL,
	bu_country_unit text NULL,
	ic_sync_mkt_campanha text NULL,
	data_de_atribuicao_pre_vendas timestamp NULL,
	mkt_sla_de_atendimento int8 NULL,
	origem_da_ultima_interacao_2_criacao_do_deal text NULL,
	sub_segmento_oficial text NULL,
	segmento_oficial text NULL,
	CONSTRAINT deals_pkey PRIMARY KEY (hs_object_id)
);
CREATE INDEX idx_deals_closedate ON public.deals USING btree (closedate);
CREATE INDEX idx_deals_createdate ON public.deals USING btree (createdate);
CREATE INDEX idx_deals_data_demonstracao ON public.deals USING btree (data_de_demonstracao);
CREATE INDEX idx_deals_dealstage ON public.deals USING btree (dealstage);
CREATE INDEX idx_deals_hs_lastmodifieddate ON public.deals USING btree (hs_lastmodifieddate);
CREATE INDEX idx_deals_hubspot_owner_id ON public.deals USING btree (hubspot_owner_id);
CREATE INDEX idx_deals_pipeline ON public.deals USING btree (pipeline);
CREATE INDEX idx_deals_pr_vendedor ON public.deals USING btree (pr_vendedor);


-- public.hubspot_properties definição

-- Drop table

-- DROP TABLE public.hubspot_properties;

CREATE TABLE public.hubspot_properties (
	id serial4 NOT NULL,
	hs_object varchar(50) NOT NULL,
	hs_name varchar(100) NOT NULL,
	hs_internal_name varchar(100) NOT NULL,
	column_db varchar(100) NOT NULL,
	table_db varchar(100) NOT NULL,
	data_type varchar(20) DEFAULT 'text'::character varying NOT NULL,
	sync_enabled bool DEFAULT true NOT NULL,
	description text NULL,
	created_at timestamptz DEFAULT now() NULL,
	updated_at timestamptz DEFAULT now() NULL,
	created_by varchar(100) NULL,
	CONSTRAINT hubspot_properties_pkey PRIMARY KEY (id)
);


-- public.line_items definição

-- Drop table

-- DROP TABLE public.line_items;

CREATE TABLE public.line_items (
	hs_object_id text NOT NULL,
	"name" text NULL,
	codigo_de_produto_omie text NULL,
	hs_sku text NULL,
	price numeric(18, 2) NULL,
	sales_bu text NULL,
	produto_principal text NULL,
	in_produto_esta_nesta_negociacao text NULL,
	hs_margin_mrr numeric(18, 2) NULL,
	description text NULL,
	adds_on text NULL,
	amount numeric(18, 2) NULL,
	discount numeric(18, 2) NULL,
	recurringbillingfrequency text NULL,
	createdate timestamp NULL,
	row_updated timestamp NULL,
	archived bool NULL,
	deal_id text NULL,
	hs_lastmodifieddate timestamp NULL,
	CONSTRAINT line_items_pkey PRIMARY KEY (hs_object_id)
);
CREATE INDEX idx_hli_deal_id ON public.line_items USING btree (deal_id);


-- public.owners definição

-- Drop table

-- DROP TABLE public.owners;

CREATE TABLE public.owners (
	userid int8 NULL,
	id varchar NOT NULL,
	email varchar NULL,
	firstname varchar NULL,
	lastname varchar NULL,
	fullname varchar NULL,
	teams jsonb NULL,
	createdat varchar NULL,
	archived varchar NULL,
	useridincludinginactive int8 NULL,
	"type" varchar NULL,
	updatedat varchar NULL,
	CONSTRAINT owners_pkey PRIMARY KEY (id)
);


-- public.sync_status definição

-- Drop table

-- DROP TABLE public.sync_status;

CREATE TABLE public.sync_status (
	id serial4 NOT NULL, -- ID único do registro
	object_type varchar(50) NOT NULL, -- Tipo de objeto (contacts, deals, companies, etc.)
	last_sync_after varchar(100) DEFAULT ''::character varying NULL, -- Cursor para paginação da API HubSpot
	total_processed int4 DEFAULT 0 NULL, -- Total de registros processados na última sincronização
	sync_date timestamp DEFAULT now() NULL, -- Data e hora da última sincronização
	status varchar(20) DEFAULT 'pending'::character varying NULL, -- Status da sincronização (pending, running, completed, error)
	created_at timestamp DEFAULT now() NULL, -- Data de criação do registro
	updated_at timestamp DEFAULT now() NULL, -- Data da última atualização
	sync_start_time timestamp NULL,
	sync_end_time timestamp NULL,
	sync_duration_seconds int4 NULL,
	properties_synced int4 DEFAULT 0 NULL,
	columns_created int4 DEFAULT 0 NULL,
	error_message text NULL,
	hubspot_cursor varchar(100) NULL,
	CONSTRAINT sync_status_pkey PRIMARY KEY (id)
);
COMMENT ON TABLE public.sync_status IS 'Controle de sincronização de objetos do HubSpot';

-- Column comments

COMMENT ON COLUMN public.sync_status.id IS 'ID único do registro';
COMMENT ON COLUMN public.sync_status.object_type IS 'Tipo de objeto (contacts, deals, companies, etc.)';
COMMENT ON COLUMN public.sync_status.last_sync_after IS 'Cursor para paginação da API HubSpot';
COMMENT ON COLUMN public.sync_status.total_processed IS 'Total de registros processados na última sincronização';
COMMENT ON COLUMN public.sync_status.sync_date IS 'Data e hora da última sincronização';
COMMENT ON COLUMN public.sync_status.status IS 'Status da sincronização (pending, running, completed, error)';
COMMENT ON COLUMN public.sync_status.created_at IS 'Data de criação do registro';
COMMENT ON COLUMN public.sync_status.updated_at IS 'Data da última atualização';

-- Table Triggers

create trigger trg_update_sync_status_updated_at before
update
    on
    public.sync_status for each row execute function update_sync_status_updated_at();


-- public.tickets definição

-- Drop table

-- DROP TABLE public.tickets;

CREATE TABLE public.tickets (
	hs_object_id int8 NOT NULL,
	am_data_de_solicitacao timestamptz NULL,
	cessao_fin_vencimento_nf text NULL,
	cessao_jur_aviso_previo_cancelamento text NULL,
	cessao_jur_forma_de_renovacao text NULL,
	cessao_jur_reajuste_anual text NULL,
	cessao_jur_rescisao_antecipada_com_multa text NULL,
	cessao_jur_vigencia_do_contrato text NULL,
	cessao_cnpj_antigo numeric(18, 2) NULL,
	cessao_cnpj_novo numeric(18, 2) NULL,
	cessao_empresa_antiga text NULL,
	cessao_empresa_nova text NULL,
	cessao_empresa_nova_ja_esta_cadastrada text NULL,
	cessao_proposta_comercial_originaria_n text NULL,
	tipo_de_pagamento_frequencia text NULL,
	cs_eventos_quem_atendeu text NULL,
	squad_css text NULL,
	cs_tipo_de_negociacao text NULL,
	cs_suporte_setor_responsavel text NULL,
	cs_suporte_tipo_de_abertura text NULL,
	cs_suporte_tipo_de_insatisfacao text NULL,
	cs_apos_qual_contato_o_cliente_pediu_cancelamento text NULL,
	bu_em_risco text NULL,
	cs_tipo_de_contato_realizado text NULL,
	classificacao_cs text NULL,
	cs_detalhamento_do_ultimo_contato text NULL,
	cs_devolutiva_analise_de_risco text NULL,
	cs_fcr_resolvido_no_mesmo_dia numeric(18, 2) NULL,
	cs_ferramenta text NULL,
	cs_observacoes_retencao_renovacao text NULL,
	cs_percentual_de_desconto_no_mrr_clonado text NULL,
	cs_produto_em_risco text NULL,
	cs_reason_code text NULL,
	cs_resultado_do_ultimo_contato text NULL,
	cs_reversao_de_perda text NULL,
	cs_risco_critico_confirmado_por_qualidade text NULL,
	cs_risco_estatistico_acao text NULL,
	cs_risco_estatistico_contagem_de_updates numeric(18, 2) NULL,
	cs_risco_estatistico_data_de_update timestamptz NULL,
	cs_risco_estatistico_data_do_risco_mapeado timestamptz NULL,
	cs_risco_estatistico_motivo_do_declinio text NULL,
	cs_risco_estatistico_probabilidade text NULL,
	cs_risco_estatistico_score text NULL,
	cs_risco_estatistico_tag_risco_mapeado text NULL,
	cs_risk_factor text NULL,
	cs_segmentacao_cs text NULL,
	cs_status_do_chamado text NULL,
	cs_suporte_premium text NULL,
	cs_time_css text NULL,
	tipo_de_solicitacao_css text NULL,
	cs_tipo_do_ticket text NULL,
	cs_valor_da_perda_intel numeric(18, 2) NULL,
	cs_valor_da_perda_supply numeric(18, 2) NULL,
	css_esta_analise_esta_relacionada_a_algum_kr text NULL,
	css_link_da_empresa_negocio_painel_relatorio text NULL,
	css_motivo_da_solicitacao text NULL,
	finops_customer_id_ticket text NULL,
	nome_guardiao text NULL,
	og_i_equipe text NULL,
	valor_da_perda numeric(18, 2) NULL,
	og_aprovador_desconto_isencao text NULL,
	og_cliente_solicitou_desconto_ou_isencao_clonado text NULL,
	og_duracao_do_desconto_isencao_clonado text NULL,
	og_mes_sem_faturamento text NULL,
	og_motivo_do_desconto_isencao_clonado text NULL,
	mrr_do_cliente_clonado numeric(18, 2) NULL,
	og_numero_da_nf_do_cliente_clonado numeric(18, 2) NULL,
	og_observacao_para_o_aprovador_clonado text NULL,
	og_origem_do_desconto_isencao_clonado text NULL,
	og_valor_a_ser_pago_pelo_cliente numeric(18, 2) NULL,
	og_valor_do_desconto_isencao_clonado numeric(18, 2) NULL,
	suporte_equipe_cs text NULL,
	gestor_css text NULL,
	suporte_squad text NULL,
	squad_em_teste text NULL,
	suporte_tipo_de_solicitacao text NULL,
	sv_acoes_de_reversao text NULL,
	sv_fator_de_reversao text NULL,
	sv_gaps_do_cliente text NULL,
	user_guardiao text NULL,
	user_guardiao_secundario text NULL,
	arquivo text NULL,
	bu_cliente text NULL,
	bu_ticket text NULL,
	caso_de_uso text NULL,
	categoria_nps text NULL,
	chamado_pre_analisado text NULL,
	chave_problema_duvida text NULL,
	data_da_pesquisa text NULL,
	data_de_resposta_nps timestamptz NULL,
	data_ultimo_e_mail_suporte timestamptz NULL,
	demanda_nao_usar_em_teste text NULL,
	nps_feedback text NULL,
	guardiao text NULL,
	indicacao_time_suporte_sales text NULL,
	si_jira_issue_assignee text NULL,
	si_jira_issue_id text NULL,
	si_jira_issue_key text NULL,
	si_jira_issue_link text NULL,
	si_jira_issue_priority text NULL,
	si_jira_issue_reporter text NULL,
	si_jira_issue_status text NULL,
	si_jira_issue_summary text NULL,
	si_jira_sync_notes text NULL,
	macro_segmento_oficial text NULL,
	modulo_em_teste text NULL,
	mrr_bu_intel numeric(18, 2) NULL,
	mrr_bu_supply numeric(18, 2) NULL,
	net_promoter_score numeric(18, 2) NULL,
	nivel text NULL,
	nome_da_empresa_associada text NULL,
	nota_do_cliente_nps text NULL,
	passagem_de_bastao_para_cs text NULL,
	segmento_oficial text NULL,
	setor text NULL,
	solucao text NULL,
	status text NULL,
	sub_segmento_oficial text NULL,
	time_do_solicitante text NULL,
	tipo_de_reuniao text NULL,
	first_agent_reply_date timestamptz NULL,
	hs_nextactivitydate timestamptz NULL,
	hs_lastactivitydate timestamptz NULL,
	hs_lastmodifieddate timestamptz NULL,
	hs_feedback_last_survey_date timestamptz NULL,
	hs_last_message_sent_at timestamptz NULL,
	last_reply_date timestamptz NULL,
	hubspot_owner_assigneddate timestamptz NULL,
	createdate timestamptz NULL,
	closed_date timestamptz NULL,
	hs_ticket_reopened_at timestamptz NULL,
	hs_last_message_received_at timestamptz NULL,
	hs_time_to_first_response_sla_at timestamptz NULL,
	hs_time_to_next_response_sla_at timestamptz NULL,
	hs_time_to_close_sla_at timestamptz NULL,
	hs_lastcontacted timestamptz NULL,
	hs_last_closed_date timestamptz NULL,
	"content" text NULL,
	hs_object_source_detail_1 text NULL,
	hs_object_source_detail_2 text NULL,
	hs_object_source_detail_3 text NULL,
	hubspot_team_id text NULL,
	hs_assigned_team_ids text NULL,
	hs_shared_team_ids text NULL,
	hs_is_closed bool NULL,
	source_type text NULL,
	hs_object_source_label text NULL,
	hs_copied_ticket_source text NULL,
	hs_ticket_id int8 NULL,
	subject text NULL,
	hs_num_associated_companies int4 NULL,
	hs_pipeline text NULL,
	hs_first_agent_message_sent_by text NULL,
	hs_ticket_priority text NULL,
	hubspot_owner_id text NULL,
	hs_resolution text NULL,
	hs_is_one_touch_ticket bool NULL,
	hs_sla_pause_status text NULL,
	hs_time_to_first_response_sla_status text NULL,
	hs_time_to_next_response_sla_status text NULL,
	hs_time_to_close_sla_status text NULL,
	hs_pipeline_stage text NULL,
	hs_customer_agent_ticket_status text NULL,
	hs_time_to_first_rep_assignment int8 NULL,
	hs_time_to_first_response_in_operating_hours int8 NULL,
	hs_time_to_close_in_operating_hours int8 NULL,
	time_to_first_agent_reply int8 NULL,
	time_to_close int8 NULL,
	CONSTRAINT tickets_pkey PRIMARY KEY (hs_object_id)
);


-- public.base_comercial_reduzida fonte

CREATE OR REPLACE VIEW public.base_comercial_reduzida
AS WITH source AS (
         SELECT d.hs_object_id,
            d.dealname,
            d.pipeline,
            d.dealstage,
            d.tipo_de_negociacao,
                CASE
                    WHEN d.tipo_de_negociacao = ANY (ARRAY['Upsell'::text, 'Cross Sell'::text]) THEN 'Upsell/CrossSell'::text
                    ELSE d.tipo_de_negociacao
                END AS "tipo_negociação_ajustada",
            d.tipo_de_receita,
            d.status_de_agendamento,
            d.produto_principal,
            d.valor_ganho,
            d.campanha,
            d.canal_de_aquisicao,
            d.coordenador,
            d.criado_por,
            d.pr_vendedor,
            d.analista_comercial,
            d.createdate::date AS createdate,
            d.data_de_entrada_na_etapa_distribuicao_vendas_nmrr,
            d.data_de_prospect,
            d.etapa_data_de_tentando_contato,
            d.data_de_qualificacao,
            d.data_de_agendamento,
            d.fase_data_de_no_show,
            d.data_de_demonstracao,
            d.data_de_proposta,
            d.etapa_data_de_entrada_em_fechamento,
            d.sales_data_de_faturamento,
            d.closedate,
            d.notes_next_activity_date,
            d.data_prevista_reuniao,
            d.notes_last_updated,
            d.hs_lastmodifieddate,
            d.faturamento_anual_ic,
            d.presales_temperatura_v2,
            d.bu_business_unit,
            d.sales_business_unit,
            d.bu_country_unit,
            d.data_de_atribuicao_pre_vendas,
            d.sales_sal_sales_accepted_lead,
            oc.fullname AS "Owners - Criado Por__fullname",
            op.fullname AS "Owners - Pr Vendedor__fullname",
            oa.fullname AS "Owners - Analista Comercial__fullname",
            oh.fullname AS "Owners - Hubspot Owner__fullname",
            st.stage_label AS "Deal Stages Pipelines - Dealstage__stage_label",
            st.deal_isclosed AS "Deal Stages Pipelines - Dealstage__deal_isclosed",
            st.pipeline_label AS "Deal Stages Pipelines - Dealstage__pipeline_label"
           FROM deals d
             LEFT JOIN owners oc ON d.criado_por = oc.id::text
             LEFT JOIN owners op ON d.pr_vendedor = op.id::text
             LEFT JOIN owners oa ON d.analista_comercial = oa.id::text
             LEFT JOIN owners oh ON d.hubspot_owner_id = oh.id::text
             LEFT JOIN deal_stages_pipelines st ON d.dealstage = st.stage_id::text
          WHERE COALESCE(d.tipo_de_receita, ''::text) <> 'Pontual'::text AND COALESCE(d.tipo_de_negociacao, ''::text) <> 'Variação Cambial'::text
         LIMIT 1048575
        )
 SELECT hs_object_id,
    dealname,
    pipeline,
    dealstage,
    tipo_de_negociacao,
    "tipo_negociação_ajustada",
    tipo_de_receita,
    status_de_agendamento,
    produto_principal,
    valor_ganho,
    campanha,
    canal_de_aquisicao,
    coordenador,
    criado_por,
    pr_vendedor,
    analista_comercial,
    createdate,
    data_de_entrada_na_etapa_distribuicao_vendas_nmrr,
    data_de_prospect,
    etapa_data_de_tentando_contato,
    data_de_qualificacao,
    data_de_agendamento,
    fase_data_de_no_show,
    data_de_demonstracao,
    data_de_proposta,
    etapa_data_de_entrada_em_fechamento,
    sales_data_de_faturamento,
    closedate,
    closedate - '03:00:00'::interval AS closedate_ajustada,
    notes_next_activity_date,
    data_prevista_reuniao,
    notes_last_updated,
    hs_lastmodifieddate,
    faturamento_anual_ic,
    presales_temperatura_v2,
    bu_business_unit,
    sales_business_unit,
    bu_country_unit,
    data_de_atribuicao_pre_vendas,
    sales_sal_sales_accepted_lead,
    "Owners - Criado Por__fullname",
    "Owners - Pr Vendedor__fullname",
    "Owners - Analista Comercial__fullname",
    "Owners - Hubspot Owner__fullname",
    "Deal Stages Pipelines - Dealstage__stage_label",
    "Deal Stages Pipelines - Dealstage__deal_isclosed",
    "Deal Stages Pipelines - Dealstage__pipeline_label",
    NULLIF(campanha, ''::text) AS "estrategia_IC",
        CASE
            WHEN sales_sal_sales_accepted_lead = ANY (ARRAY['Qualificada'::text, 'Oportunidade forte, alta prioridade'::text, 'Boa oportunidade, mas precisa de maturação'::text]) THEN 'Sim'::text
            ELSE 'Não'::text
        END AS sales_sal_qualificada
   FROM source s
 LIMIT 1048575;


-- public.projeto_pricing fonte

CREATE OR REPLACE VIEW public.projeto_pricing
AS SELECT d.hs_object_id,
    d.dealname,
    p.stage_label,
    p.pipeline_label,
    d.valor_ganho,
    l.codigo_de_produto_omie,
    l.name,
    l.price AS full_price,
    l.discount,
    l.hs_margin_mrr AS margin_mrr,
    l.description,
    l.hs_margin_mrr AS margin_mrr_item,
    d.canal_de_aquisicao,
    d.faturamento_anual_ic,
    d.closedate,
    d.macro_segmento_oficial
   FROM deals d
     LEFT JOIN deal_stages_pipelines p ON d.pipeline = p.pipeline_id::text
     LEFT JOIN deal_stages_pipelines s ON d.dealstage = s.stage_id::text
     LEFT JOIN line_items l ON d.hs_object_id = l.deal_id
  WHERE p.stage_label = 'Ganho'::text AND d.pipeline = '6810518'::text;



-- DROP FUNCTION public.array_to_halfvec(_float8, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_halfvec(double precision[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
;

-- DROP FUNCTION public.array_to_halfvec(_int4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_halfvec(integer[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
;

-- DROP FUNCTION public.array_to_halfvec(_float4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_halfvec(real[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
;

-- DROP FUNCTION public.array_to_halfvec(_numeric, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_halfvec(numeric[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
;

-- DROP FUNCTION public.array_to_sparsevec(_int4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_sparsevec(integer[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
;

-- DROP FUNCTION public.array_to_sparsevec(_numeric, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_sparsevec(numeric[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
;

-- DROP FUNCTION public.array_to_sparsevec(_float8, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_sparsevec(double precision[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
;

-- DROP FUNCTION public.array_to_sparsevec(_float4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_sparsevec(real[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
;

-- DROP FUNCTION public.array_to_vector(_numeric, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_vector(numeric[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
;

-- DROP FUNCTION public.array_to_vector(_int4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_vector(integer[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
;

-- DROP FUNCTION public.array_to_vector(_float8, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_vector(double precision[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
;

-- DROP FUNCTION public.array_to_vector(_float4, int4, bool);

CREATE OR REPLACE FUNCTION public.array_to_vector(real[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
;

-- DROP AGGREGATE public.avg(vector);

-- Aggregate function public.avg(vector)
-- ERROR: more than one function named "public.avg";

-- DROP AGGREGATE public.avg(halfvec);

-- Aggregate function public.avg(halfvec)
-- ERROR: more than one function named "public.avg";

-- DROP FUNCTION public.binary_quantize(vector);

CREATE OR REPLACE FUNCTION public.binary_quantize(vector)
 RETURNS bit
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$binary_quantize$function$
;

-- DROP FUNCTION public.binary_quantize(halfvec);

CREATE OR REPLACE FUNCTION public.binary_quantize(halfvec)
 RETURNS bit
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_binary_quantize$function$
;

-- DROP FUNCTION public.cosine_distance(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.cosine_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_cosine_distance$function$
;

-- DROP FUNCTION public.cosine_distance(vector, vector);

CREATE OR REPLACE FUNCTION public.cosine_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$cosine_distance$function$
;

-- DROP FUNCTION public.cosine_distance(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.cosine_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_cosine_distance$function$
;

-- DROP FUNCTION public.halfvec(halfvec, int4, bool);

CREATE OR REPLACE FUNCTION public.halfvec(halfvec, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec$function$
;

-- DROP FUNCTION public.halfvec_accum(_float8, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_accum(double precision[], halfvec)
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_accum$function$
;

-- DROP FUNCTION public.halfvec_add(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_add(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_add$function$
;

-- DROP FUNCTION public.halfvec_avg(_float8);

CREATE OR REPLACE FUNCTION public.halfvec_avg(double precision[])
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_avg$function$
;

-- DROP FUNCTION public.halfvec_cmp(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_cmp(halfvec, halfvec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_cmp$function$
;

-- DROP FUNCTION public.halfvec_combine(_float8, _float8);

CREATE OR REPLACE FUNCTION public.halfvec_combine(double precision[], double precision[])
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_combine$function$
;

-- DROP FUNCTION public.halfvec_concat(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_concat(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_concat$function$
;

-- DROP FUNCTION public.halfvec_eq(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_eq(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_eq$function$
;

-- DROP FUNCTION public.halfvec_ge(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_ge(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_ge$function$
;

-- DROP FUNCTION public.halfvec_gt(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_gt(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_gt$function$
;

-- DROP FUNCTION public.halfvec_in(cstring, oid, int4);

CREATE OR REPLACE FUNCTION public.halfvec_in(cstring, oid, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_in$function$
;

-- DROP FUNCTION public.halfvec_l2_squared_distance(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_l2_squared_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_squared_distance$function$
;

-- DROP FUNCTION public.halfvec_le(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_le(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_le$function$
;

-- DROP FUNCTION public.halfvec_lt(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_lt(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_lt$function$
;

-- DROP FUNCTION public.halfvec_mul(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_mul(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_mul$function$
;

-- DROP FUNCTION public.halfvec_ne(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_ne(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_ne$function$
;

-- DROP FUNCTION public.halfvec_negative_inner_product(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_negative_inner_product(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_negative_inner_product$function$
;

-- DROP FUNCTION public.halfvec_out(halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_out(halfvec)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_out$function$
;

-- DROP FUNCTION public.halfvec_recv(internal, oid, int4);

CREATE OR REPLACE FUNCTION public.halfvec_recv(internal, oid, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_recv$function$
;

-- DROP FUNCTION public.halfvec_send(halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_send(halfvec)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_send$function$
;

-- DROP FUNCTION public.halfvec_spherical_distance(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_spherical_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_spherical_distance$function$
;

-- DROP FUNCTION public.halfvec_sub(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.halfvec_sub(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_sub$function$
;

-- DROP FUNCTION public.halfvec_to_float4(halfvec, int4, bool);

CREATE OR REPLACE FUNCTION public.halfvec_to_float4(halfvec, integer, boolean)
 RETURNS real[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_float4$function$
;

-- DROP FUNCTION public.halfvec_to_sparsevec(halfvec, int4, bool);

CREATE OR REPLACE FUNCTION public.halfvec_to_sparsevec(halfvec, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_sparsevec$function$
;

-- DROP FUNCTION public.halfvec_to_vector(halfvec, int4, bool);

CREATE OR REPLACE FUNCTION public.halfvec_to_vector(halfvec, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_vector$function$
;

-- DROP FUNCTION public.halfvec_typmod_in(_cstring);

CREATE OR REPLACE FUNCTION public.halfvec_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_typmod_in$function$
;

-- DROP FUNCTION public.hamming_distance(bit, bit);

CREATE OR REPLACE FUNCTION public.hamming_distance(bit, bit)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$hamming_distance$function$
;

-- DROP FUNCTION public.hnsw_bit_support(internal);

CREATE OR REPLACE FUNCTION public.hnsw_bit_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_bit_support$function$
;

-- DROP FUNCTION public.hnsw_halfvec_support(internal);

CREATE OR REPLACE FUNCTION public.hnsw_halfvec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_halfvec_support$function$
;

-- DROP FUNCTION public.hnsw_sparsevec_support(internal);

CREATE OR REPLACE FUNCTION public.hnsw_sparsevec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_sparsevec_support$function$
;

-- DROP FUNCTION public.hnswhandler(internal);

CREATE OR REPLACE FUNCTION public.hnswhandler(internal)
 RETURNS index_am_handler
 LANGUAGE c
AS '$libdir/vector', $function$hnswhandler$function$
;

-- DROP FUNCTION public.inner_product(vector, vector);

CREATE OR REPLACE FUNCTION public.inner_product(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$inner_product$function$
;

-- DROP FUNCTION public.inner_product(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.inner_product(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_inner_product$function$
;

-- DROP FUNCTION public.inner_product(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.inner_product(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_inner_product$function$
;

-- DROP FUNCTION public.ivfflat_bit_support(internal);

CREATE OR REPLACE FUNCTION public.ivfflat_bit_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$ivfflat_bit_support$function$
;

-- DROP FUNCTION public.ivfflat_halfvec_support(internal);

CREATE OR REPLACE FUNCTION public.ivfflat_halfvec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$ivfflat_halfvec_support$function$
;

-- DROP FUNCTION public.ivfflathandler(internal);

CREATE OR REPLACE FUNCTION public.ivfflathandler(internal)
 RETURNS index_am_handler
 LANGUAGE c
AS '$libdir/vector', $function$ivfflathandler$function$
;

-- DROP FUNCTION public.jaccard_distance(bit, bit);

CREATE OR REPLACE FUNCTION public.jaccard_distance(bit, bit)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$jaccard_distance$function$
;

-- DROP FUNCTION public.l1_distance(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.l1_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l1_distance$function$
;

-- DROP FUNCTION public.l1_distance(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.l1_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l1_distance$function$
;

-- DROP FUNCTION public.l1_distance(vector, vector);

CREATE OR REPLACE FUNCTION public.l1_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l1_distance$function$
;

-- DROP FUNCTION public.l2_distance(halfvec, halfvec);

CREATE OR REPLACE FUNCTION public.l2_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_distance$function$
;

-- DROP FUNCTION public.l2_distance(vector, vector);

CREATE OR REPLACE FUNCTION public.l2_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l2_distance$function$
;

-- DROP FUNCTION public.l2_distance(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.l2_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_distance$function$
;

-- DROP FUNCTION public.l2_norm(halfvec);

CREATE OR REPLACE FUNCTION public.l2_norm(halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_norm$function$
;

-- DROP FUNCTION public.l2_norm(sparsevec);

CREATE OR REPLACE FUNCTION public.l2_norm(sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_norm$function$
;

-- DROP FUNCTION public.l2_normalize(sparsevec);

CREATE OR REPLACE FUNCTION public.l2_normalize(sparsevec)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_normalize$function$
;

-- DROP FUNCTION public.l2_normalize(halfvec);

CREATE OR REPLACE FUNCTION public.l2_normalize(halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_normalize$function$
;

-- DROP FUNCTION public.l2_normalize(vector);

CREATE OR REPLACE FUNCTION public.l2_normalize(vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l2_normalize$function$
;

-- DROP FUNCTION public.sparsevec(sparsevec, int4, bool);

CREATE OR REPLACE FUNCTION public.sparsevec(sparsevec, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec$function$
;

-- DROP FUNCTION public.sparsevec_cmp(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_cmp(sparsevec, sparsevec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_cmp$function$
;

-- DROP FUNCTION public.sparsevec_eq(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_eq(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_eq$function$
;

-- DROP FUNCTION public.sparsevec_ge(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_ge(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_ge$function$
;

-- DROP FUNCTION public.sparsevec_gt(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_gt(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_gt$function$
;

-- DROP FUNCTION public.sparsevec_in(cstring, oid, int4);

CREATE OR REPLACE FUNCTION public.sparsevec_in(cstring, oid, integer)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_in$function$
;

-- DROP FUNCTION public.sparsevec_l2_squared_distance(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_l2_squared_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_squared_distance$function$
;

-- DROP FUNCTION public.sparsevec_le(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_le(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_le$function$
;

-- DROP FUNCTION public.sparsevec_lt(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_lt(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_lt$function$
;

-- DROP FUNCTION public.sparsevec_ne(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_ne(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_ne$function$
;

-- DROP FUNCTION public.sparsevec_negative_inner_product(sparsevec, sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_negative_inner_product(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_negative_inner_product$function$
;

-- DROP FUNCTION public.sparsevec_out(sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_out(sparsevec)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_out$function$
;

-- DROP FUNCTION public.sparsevec_recv(internal, oid, int4);

CREATE OR REPLACE FUNCTION public.sparsevec_recv(internal, oid, integer)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_recv$function$
;

-- DROP FUNCTION public.sparsevec_send(sparsevec);

CREATE OR REPLACE FUNCTION public.sparsevec_send(sparsevec)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_send$function$
;

-- DROP FUNCTION public.sparsevec_to_halfvec(sparsevec, int4, bool);

CREATE OR REPLACE FUNCTION public.sparsevec_to_halfvec(sparsevec, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_to_halfvec$function$
;

-- DROP FUNCTION public.sparsevec_to_vector(sparsevec, int4, bool);

CREATE OR REPLACE FUNCTION public.sparsevec_to_vector(sparsevec, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_to_vector$function$
;

-- DROP FUNCTION public.sparsevec_typmod_in(_cstring);

CREATE OR REPLACE FUNCTION public.sparsevec_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_typmod_in$function$
;

-- DROP FUNCTION public.subvector(vector, int4, int4);

CREATE OR REPLACE FUNCTION public.subvector(vector, integer, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$subvector$function$
;

-- DROP FUNCTION public.subvector(halfvec, int4, int4);

CREATE OR REPLACE FUNCTION public.subvector(halfvec, integer, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_subvector$function$
;

-- DROP AGGREGATE public.sum(vector);

-- Aggregate function public.sum(vector)
-- ERROR: more than one function named "public.sum";

-- DROP AGGREGATE public.sum(halfvec);

-- Aggregate function public.sum(halfvec)
-- ERROR: more than one function named "public.sum";

-- DROP FUNCTION public.update_contact_sync_timestamp();

CREATE OR REPLACE FUNCTION public.update_contact_sync_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.last_sync_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

-- DROP FUNCTION public.update_contact_updated_at();

CREATE OR REPLACE FUNCTION public.update_contact_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

-- DROP FUNCTION public.update_sync_status_updated_at();

CREATE OR REPLACE FUNCTION public.update_sync_status_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$
;

-- DROP FUNCTION public.upsert_company(jsonb);

CREATE OR REPLACE FUNCTION public.upsert_company(data jsonb)
 RETURNS bigint
 LANGUAGE plpgsql
AS $function$
DECLARE
  result_id bigint;
BEGIN
  INSERT INTO public.companies (
    hs_object_id, name, domain, cnpj, createdate, hs_lastmodifieddate, notes_last_updated,
    segmento_1, segmento_2, segmento_3, country, phone, lifecyclestage, status_da_empresa,
    faturamento_anual_ic, cnpj_situacao_cadastral_ic, cnae_id, cnae,
    score_de_credito_categoria, score_de_credito_detalhes, score_de_credito_ultima_atualizacao,
    fob_anual_ic, num_associated_contacts, num_associated_deals, hs_num_open_deals,
    address, address2, am_data_de_solicitacao, aut_customer_health_status_cs,
    aut_ob_flag_acionada_cs, bu_cliente, bu_guardiao_secundario, city,
    classificacao_cs, classificacao_mrr_bu_is, classificacao_mrr_bu_os, cliente_automacao,
    closed_won_reason_cs, cnpj_gerador_de_leads, codigo_hs, contrato_valor_total_recorrente,
    cs_abrir_card_no_hubspot_cs, cs_cumprindo_aviso_previo_clonado, cs_data_do_ultimo_risco_mapeado,
    cs_emissao_de_nf_clonado, cs_etapa_no_pipeline_de_risco, cs_exp_cargo_do_solicitante,
    cs_exp_contato_solicitante, cs_exp_detalhes_da_oportunidade, cs_exp_origem_nova_receita,
    cs_exp_prioridade_de_contato, cs_inadimplencia_qtd_de_notas, cs_origem_da_perda,
    cs_possui_negocio_aberto_em_perda, cs_potencial_expansao, cs_segmentacao_cs,
    cs_suporte_premium, cs_tickets_nos_ultimos_30_dias, data_do_ultimo_perdido,
    duracao_da_implementacao, empresa_de_grupo_economico, empresa_estrangeira, etapa_em_perda,
    ev_maturidade_do_cliente, faturamento_anual_em_dolares_usd, faturamento_dividido,
    fin_data_de_pagamento_clonado, fin_faturamento_padrao_clonado, fin_forma_de_pagamento_clonado,
    fin_tem_pedido_de_compra, fin_tipo_de_faturamento_clonado, fin_vencimento_nf,
    health_score_acessos, health_score_ces, health_score_crescimento_cliente,
    health_score_inadimplencia, health_score_interacao_cliente, health_score_nota,
    health_score_nps, health_score_sem_sentimento, health_score_sentimento,
    health_score_tickets_outros, health_score_tickets_problema, health_score_usa_logmanager,
    health_score_usa_logtracking, health_score_usa_ncm, health_score_usa_shipment,
    health_score_usabilidade_geral, hs_country_code, hs_updated_by_user_id,
    hubspot_owner_assigneddate, hubspot_owner_id, hubspot_team_id, id_lead, id_logcomex,
    idioma_do_cliente, implementador, implementador_cross_sell, jur_aviso_previo_cancelamento,
    jur_forma_de_renovacao, jur_reajuste_anual, jur_rescisao_antecipada_com_multa,
    jur_vigencia_do_contrato, mat_area_preparada_para_dado, mat_especializacao_em_comex,
    mat_nivel_utilizacao_de_dado, mkt_cliente_ativo, mkt_cliente_internacional, mkt_cnpj,
    mkt_nome_da_empresa, mkt_produtos_ativos, mrr_bu_intelligence, mrr_bu_operational, mrr_r,
    numberofemployees, ob_aud_auditoria_cliente_e_contrato, ob_aud_auditoria_engajamento_do_cliente,
    ob_aud_auditoria_insatisfacoes_e_problemas_clonado, ob_aud_auditoria_maturidade_do_cliente,
    ob_aud_auditoria_observacao_red_flags, ob_aud_auditoria_observacao_yellow_flags,
    ob_aud_observacoes_yellow_flag_in, ob_aud_yellow_flags_in_clonado,
    ob_aud_yellow_flags_out_clonado, ob_casos_de_uso, ob_data_de_agendamento_clonado,
    ob_data_de_kickoff, ob_i_classificacao_do_cliente, ob_i_cliente_liberado_sem_pgto,
    ob_i_conclusao_da_implementacao, ob_i_frequencia_de_usabilidade,
    ob_i_inicio_da_implementacao, ob_i_status_do_onboarding, ob_maturidade_do_cliente,
    ob_mostrou_risco_de_cancelar, ob_observacoes_red_flag_cs, ob_qtde_de_usuarios,
    ob_tipo_de_onboarding, obj_a_log_atende_o_objetivo_cs, obj_a_log_esta_contribuindo_cs,
    obj_estrategia_para_objetivo_cs, obj_nivel_de_atingimento_cs, obj_objetivo_com_o_produto_cs,
    obj_satisfacao_atingimento_cs, obj_tem_clareza_no_objetivo, og_cliente_sinalizou_perda,
    og_aut_maturidade_do_cliente, og_equipe_secundaria, og_reversao_de_perda,
    og_status_da_aprovacao_desconto_isencao_clonado, og_valor_revertido, ops_client_success,
    origem_da_empresa, pais_menu_suspenso, pais_de_operacao_principal, passagem_de_bastao_para_cs,
    quantidade_de_exportadores, sales_alteracao_no_plano_padrao, sales_isencao_de_pagamento_carencia,
    sales_percentual_de_desconto_no_mrr, sales_percentual_desconto_onboarding,
    sales_recuperacao_judicial, sales_venda_para_cpf, score_empresa_inadimplente,
    sdr_maturidade_do_cliente, state, sv_acoes_para_reversao, tipo_de_pagamento_frequencia,
    user_guardiao, user_guardiao_secundario, user_quality, valor_cif, website, zip
  )
  VALUES (
    NULLIF(data->>'hs_object_id', '')::bigint,
    NULLIF(data->>'name', ''),
    NULLIF(data->>'domain', ''),
    NULLIF(data->>'cnpj', ''),
    NULLIF(data->>'createdate', '')::timestamp with time zone,
    NULLIF(data->>'hs_lastmodifieddate', '')::timestamp with time zone,
    NULLIF(data->>'notes_last_updated', '')::timestamp with time zone,
    NULLIF(data->>'segmento_1', ''),
    NULLIF(data->>'segmento_2', ''),
    NULLIF(data->>'segmento_3', ''),
    NULLIF(data->>'country', ''),
    NULLIF(data->>'phone', ''),
    NULLIF(data->>'lifecyclestage', ''),
    NULLIF(data->>'status_da_empresa', ''),
    NULLIF(data->>'faturamento_anual_ic', ''),
    NULLIF(data->>'cnpj_situacao_cadastral_ic', ''),
    NULLIF(data->>'cnae_id', ''),
    NULLIF(data->>'cnae', ''),
    NULLIF(data->>'score_de_credito_categoria', ''),
    NULLIF(data->>'score_de_credito_detalhes', ''),
    NULLIF(data->>'score_de_credito_ultima_atualizacao', '')::timestamp with time zone,
    NULLIF(data->>'fob_anual_ic', ''),
    NULLIF(data->>'num_associated_contacts', '')::integer,
    NULLIF(data->>'num_associated_deals', '')::integer,
    NULLIF(data->>'hs_num_open_deals', '')::integer,
    NULLIF(data->>'address', ''),
    NULLIF(data->>'address2', ''),
    NULLIF(data->>'am_data_de_solicitacao', '')::timestamp with time zone,
    NULLIF(data->>'aut_customer_health_status_cs', ''),
    NULLIF(data->>'aut_ob_flag_acionada_cs', ''),
    NULLIF(data->>'bu_cliente', ''),
    NULLIF(data->>'bu_guardiao_secundario', ''),
    NULLIF(data->>'city', ''),
    NULLIF(data->>'classificacao_cs', ''),
    NULLIF(data->>'classificacao_mrr_bu_is', ''),
    NULLIF(data->>'classificacao_mrr_bu_os', ''),
    NULLIF(data->>'cliente_automacao', ''),
    NULLIF(data->>'closed_won_reason_cs', ''),
    NULLIF(data->>'cnpj_gerador_de_leads', ''),
    NULLIF(data->>'codigo_hs', ''),
    NULLIF(data->>'contrato_valor_total_recorrente', '')::numeric,
    NULLIF(data->>'cs_abrir_card_no_hubspot_cs', ''),
    NULLIF(data->>'cs_cumprindo_aviso_previo_clonado', ''),
    NULLIF(data->>'cs_data_do_ultimo_risco_mapeado', '')::timestamp with time zone,
    NULLIF(data->>'cs_emissao_de_nf_clonado', ''),
    NULLIF(data->>'cs_etapa_no_pipeline_de_risco', ''),
    NULLIF(data->>'cs_exp_cargo_do_solicitante', ''),
    NULLIF(data->>'cs_exp_contato_solicitante', ''),
    NULLIF(data->>'cs_exp_detalhes_da_oportunidade', ''),
    NULLIF(data->>'cs_exp_origem_nova_receita', ''),
    NULLIF(data->>'cs_exp_prioridade_de_contato', ''),
    NULLIF(data->>'cs_inadimplencia_qtd_de_notas', '')::integer,
    NULLIF(data->>'cs_origem_da_perda', ''),
    NULLIF(data->>'cs_possui_negocio_aberto_em_perda', ''),
    NULLIF(data->>'cs_potencial_expansao', ''),
    NULLIF(data->>'cs_segmentacao_cs', ''),
    NULLIF(data->>'cs_suporte_premium', ''),
    NULLIF(data->>'cs_tickets_nos_ultimos_30_dias', '')::integer,
    NULLIF(data->>'data_do_ultimo_perdido', '')::timestamp with time zone,
    NULLIF(data->>'duracao_da_implementacao', '')::numeric,
    NULLIF(data->>'empresa_de_grupo_economico', ''),
    NULLIF(data->>'empresa_estrangeira', ''),
    NULLIF(data->>'etapa_em_perda', ''),
    NULLIF(data->>'ev_maturidade_do_cliente', ''),
    NULLIF(data->>'faturamento_anual_em_dolares_usd', ''),
    NULLIF(data->>'faturamento_dividido', ''),
    NULLIF(data->>'fin_data_de_pagamento_clonado', '')::timestamp with time zone,
    NULLIF(data->>'fin_faturamento_padrao_clonado', ''),
    NULLIF(data->>'fin_forma_de_pagamento_clonado', ''),
    NULLIF(data->>'fin_tem_pedido_de_compra', ''),
    NULLIF(data->>'fin_tipo_de_faturamento_clonado', ''),
    NULLIF(data->>'fin_vencimento_nf', ''),
    NULLIF(data->>'health_score_acessos', '')::numeric,
    NULLIF(data->>'health_score_ces', '')::numeric,
    NULLIF(data->>'health_score_crescimento_cliente', '')::numeric,
    NULLIF(data->>'health_score_inadimplencia', '')::numeric,
    NULLIF(data->>'health_score_interacao_cliente', '')::numeric,
    NULLIF(data->>'health_score_nota', '')::numeric,
    NULLIF(data->>'health_score_nps', '')::numeric,
    NULLIF(data->>'health_score_sem_sentimento', '')::numeric,
    NULLIF(data->>'health_score_sentimento', '')::numeric,
    NULLIF(data->>'health_score_tickets_outros', '')::numeric,
    NULLIF(data->>'health_score_tickets_problema', '')::numeric,
    NULLIF(data->>'health_score_usa_logmanager', '')::numeric,
    NULLIF(data->>'health_score_usa_logtracking', '')::numeric,
    NULLIF(data->>'health_score_usa_ncm', '')::numeric,
    NULLIF(data->>'health_score_usa_shipment', '')::numeric,
    NULLIF(data->>'health_score_usabilidade_geral', '')::numeric,
    NULLIF(data->>'hs_country_code', ''),
    NULLIF(data->>'hs_updated_by_user_id', '')::bigint,
    NULLIF(data->>'hubspot_owner_assigneddate', '')::timestamp with time zone,
    NULLIF(data->>'hubspot_owner_id', ''),
    NULLIF(data->>'hubspot_team_id', ''),
    NULLIF(data->>'id_lead', ''),
    NULLIF(data->>'id_logcomex', ''),
    NULLIF(data->>'idioma_do_cliente', ''),
    NULLIF(data->>'implementador', ''),
    NULLIF(data->>'implementador_cross_sell', ''),
    NULLIF(data->>'jur_aviso_previo_cancelamento', ''),
    NULLIF(data->>'jur_forma_de_renovacao', ''),
    NULLIF(data->>'jur_reajuste_anual', ''),
    NULLIF(data->>'jur_rescisao_antecipada_com_multa', ''),
    NULLIF(data->>'jur_vigencia_do_contrato', ''),
    NULLIF(data->>'mat_area_preparada_para_dado', ''),
    NULLIF(data->>'mat_especializacao_em_comex', ''),
    NULLIF(data->>'mat_nivel_utilizacao_de_dado', ''),
    NULLIF(data->>'mkt_cliente_ativo', ''),
    NULLIF(data->>'mkt_cliente_internacional', ''),
    NULLIF(data->>'mkt_cnpj', ''),
    NULLIF(data->>'mkt_nome_da_empresa', ''),
    NULLIF(data->>'mkt_produtos_ativos', ''),
    NULLIF(data->>'mrr_bu_intelligence', '')::numeric,
    NULLIF(data->>'mrr_bu_operational', '')::numeric,
    NULLIF(data->>'mrr_r', '')::numeric,
    NULLIF(data->>'numberofemployees', '')::integer,
    NULLIF(data->>'ob_aud_auditoria_cliente_e_contrato', ''),
    NULLIF(data->>'ob_aud_auditoria_engajamento_do_cliente', ''),
    NULLIF(data->>'ob_aud_auditoria_insatisfacoes_e_problemas_clonado', ''),
    NULLIF(data->>'ob_aud_auditoria_maturidade_do_cliente', ''),
    NULLIF(data->>'ob_aud_auditoria_observacao_red_flags', ''),
    NULLIF(data->>'ob_aud_auditoria_observacao_yellow_flags', ''),
    NULLIF(data->>'ob_aud_observacoes_yellow_flag_in', ''),
    NULLIF(data->>'ob_aud_yellow_flags_in_clonado', ''),
    NULLIF(data->>'ob_aud_yellow_flags_out_clonado', ''),
    NULLIF(data->>'ob_casos_de_uso', ''),
    NULLIF(data->>'ob_data_de_agendamento_clonado', '')::timestamp with time zone,
    NULLIF(data->>'ob_data_de_kickoff', '')::timestamp with time zone,
    NULLIF(data->>'ob_i_classificacao_do_cliente', ''),
    NULLIF(data->>'ob_i_cliente_liberado_sem_pgto', ''),
    NULLIF(data->>'ob_i_conclusao_da_implementacao', '')::timestamp with time zone,
    NULLIF(data->>'ob_i_frequencia_de_usabilidade', ''),
    NULLIF(data->>'ob_i_inicio_da_implementacao', '')::timestamp with time zone,
    NULLIF(data->>'ob_i_status_do_onboarding', ''),
    NULLIF(data->>'ob_maturidade_do_cliente', ''),
    NULLIF(data->>'ob_mostrou_risco_de_cancelar', ''),
    NULLIF(data->>'ob_observacoes_red_flag_cs', ''),
    NULLIF(data->>'ob_qtde_de_usuarios', '')::integer,
    NULLIF(data->>'ob_tipo_de_onboarding', ''),
    NULLIF(data->>'obj_a_log_atende_o_objetivo_cs', ''),
    NULLIF(data->>'obj_a_log_esta_contribuindo_cs', ''),
    NULLIF(data->>'obj_estrategia_para_objetivo_cs', ''),
    NULLIF(data->>'obj_nivel_de_atingimento_cs', ''),
    NULLIF(data->>'obj_objetivo_com_o_produto_cs', ''),
    NULLIF(data->>'obj_satisfacao_atingimento_cs', ''),
    NULLIF(data->>'obj_tem_clareza_no_objetivo', ''),
    NULLIF(data->>'og_cliente_sinalizou_perda', ''),
    NULLIF(data->>'og_aut_maturidade_do_cliente', ''),
    NULLIF(data->>'og_equipe_secundaria', ''),
    NULLIF(data->>'og_reversao_de_perda', ''),
    NULLIF(data->>'og_status_da_aprovacao_desconto_isencao_clonado', ''),
    NULLIF(data->>'og_valor_revertido', '')::numeric,
    NULLIF(data->>'ops_client_success', ''),
    NULLIF(data->>'origem_da_empresa', ''),
    NULLIF(data->>'pais_menu_suspenso', ''),
    NULLIF(data->>'pais_de_operacao_principal', ''),
    NULLIF(data->>'passagem_de_bastao_para_cs', ''),
    NULLIF(data->>'quantidade_de_exportadores', '')::integer,
    NULLIF(data->>'sales_alteracao_no_plano_padrao', ''),
    NULLIF(data->>'sales_isencao_de_pagamento_carencia', ''),
    NULLIF(data->>'sales_percentual_de_desconto_no_mrr', ''),
    NULLIF(data->>'sales_percentual_desconto_onboarding', ''),
    NULLIF(data->>'sales_recuperacao_judicial', ''),
    NULLIF(data->>'sales_venda_para_cpf', ''),
    NULLIF(data->>'score_empresa_inadimplente', ''),
    NULLIF(data->>'sdr_maturidade_do_cliente', ''),
    NULLIF(data->>'state', ''),
    NULLIF(data->>'sv_acoes_para_reversao', ''),
    NULLIF(data->>'tipo_de_pagamento_frequencia', ''),
    NULLIF(data->>'user_guardiao', ''),
    NULLIF(data->>'user_guardiao_secundario', ''),
    NULLIF(data->>'user_quality', ''),
    NULLIF(data->>'valor_cif', '')::numeric,
    NULLIF(data->>'website', ''),
    NULLIF(data->>'zip', '')
  )
  ON CONFLICT (hs_object_id) DO UPDATE SET
    name = EXCLUDED.name,
    domain = EXCLUDED.domain,
    cnpj = EXCLUDED.cnpj,
    createdate = EXCLUDED.createdate,
    hs_lastmodifieddate = EXCLUDED.hs_lastmodifieddate,
    notes_last_updated = EXCLUDED.notes_last_updated,
    segmento_1 = EXCLUDED.segmento_1,
    segmento_2 = EXCLUDED.segmento_2,
    segmento_3 = EXCLUDED.segmento_3,
    country = EXCLUDED.country,
    phone = EXCLUDED.phone,
    lifecyclestage = EXCLUDED.lifecyclestage,
    status_da_empresa = EXCLUDED.status_da_empresa,
    faturamento_anual_ic = EXCLUDED.faturamento_anual_ic,
    cnpj_situacao_cadastral_ic = EXCLUDED.cnpj_situacao_cadastral_ic,
    cnae_id = EXCLUDED.cnae_id,
    cnae = EXCLUDED.cnae,
    score_de_credito_categoria = EXCLUDED.score_de_credito_categoria,
    score_de_credito_detalhes = EXCLUDED.score_de_credito_detalhes,
    score_de_credito_ultima_atualizacao = EXCLUDED.score_de_credito_ultima_atualizacao,
    fob_anual_ic = EXCLUDED.fob_anual_ic,
    num_associated_contacts = EXCLUDED.num_associated_contacts,
    num_associated_deals = EXCLUDED.num_associated_deals,
    hs_num_open_deals = EXCLUDED.hs_num_open_deals,
    address = EXCLUDED.address,
    address2 = EXCLUDED.address2,
    am_data_de_solicitacao = EXCLUDED.am_data_de_solicitacao,
    aut_customer_health_status_cs = EXCLUDED.aut_customer_health_status_cs,
    aut_ob_flag_acionada_cs = EXCLUDED.aut_ob_flag_acionada_cs,
    bu_cliente = EXCLUDED.bu_cliente,
    bu_guardiao_secundario = EXCLUDED.bu_guardiao_secundario,
    city = EXCLUDED.city,
    classificacao_cs = EXCLUDED.classificacao_cs,
    classificacao_mrr_bu_is = EXCLUDED.classificacao_mrr_bu_is,
    classificacao_mrr_bu_os = EXCLUDED.classificacao_mrr_bu_os,
    cliente_automacao = EXCLUDED.cliente_automacao,
    closed_won_reason_cs = EXCLUDED.closed_won_reason_cs,
    cnpj_gerador_de_leads = EXCLUDED.cnpj_gerador_de_leads,
    codigo_hs = EXCLUDED.codigo_hs,
    contrato_valor_total_recorrente = EXCLUDED.contrato_valor_total_recorrente,
    cs_abrir_card_no_hubspot_cs = EXCLUDED.cs_abrir_card_no_hubspot_cs,
    cs_cumprindo_aviso_previo_clonado = EXCLUDED.cs_cumprindo_aviso_previo_clonado,
    cs_data_do_ultimo_risco_mapeado = EXCLUDED.cs_data_do_ultimo_risco_mapeado,
    cs_emissao_de_nf_clonado = EXCLUDED.cs_emissao_de_nf_clonado,
    cs_etapa_no_pipeline_de_risco = EXCLUDED.cs_etapa_no_pipeline_de_risco,
    cs_exp_cargo_do_solicitante = EXCLUDED.cs_exp_cargo_do_solicitante,
    cs_exp_contato_solicitante = EXCLUDED.cs_exp_contato_solicitante,
    cs_exp_detalhes_da_oportunidade = EXCLUDED.cs_exp_detalhes_da_oportunidade,
    cs_exp_origem_nova_receita = EXCLUDED.cs_exp_origem_nova_receita,
    cs_exp_prioridade_de_contato = EXCLUDED.cs_exp_prioridade_de_contato,
    cs_inadimplencia_qtd_de_notas = EXCLUDED.cs_inadimplencia_qtd_de_notas,
    cs_origem_da_perda = EXCLUDED.cs_origem_da_perda,
    cs_possui_negocio_aberto_em_perda = EXCLUDED.cs_possui_negocio_aberto_em_perda,
    cs_potencial_expansao = EXCLUDED.cs_potencial_expansao,
    cs_segmentacao_cs = EXCLUDED.cs_segmentacao_cs,
    cs_suporte_premium = EXCLUDED.cs_suporte_premium,
    cs_tickets_nos_ultimos_30_dias = EXCLUDED.cs_tickets_nos_ultimos_30_dias,
    data_do_ultimo_perdido = EXCLUDED.data_do_ultimo_perdido,
    duracao_da_implementacao = EXCLUDED.duracao_da_implementacao,
    empresa_de_grupo_economico = EXCLUDED.empresa_de_grupo_economico,
    empresa_estrangeira = EXCLUDED.empresa_estrangeira,
    etapa_em_perda = EXCLUDED.etapa_em_perda,
    ev_maturidade_do_cliente = EXCLUDED.ev_maturidade_do_cliente,
    faturamento_anual_em_dolares_usd = EXCLUDED.faturamento_anual_em_dolares_usd,
    faturamento_dividido = EXCLUDED.faturamento_dividido,
    fin_data_de_pagamento_clonado = EXCLUDED.fin_data_de_pagamento_clonado,
    fin_faturamento_padrao_clonado = EXCLUDED.fin_faturamento_padrao_clonado,
    fin_forma_de_pagamento_clonado = EXCLUDED.fin_forma_de_pagamento_clonado,
    fin_tem_pedido_de_compra = EXCLUDED.fin_tem_pedido_de_compra,
    fin_tipo_de_faturamento_clonado = EXCLUDED.fin_tipo_de_faturamento_clonado,
    fin_vencimento_nf = EXCLUDED.fin_vencimento_nf,
    health_score_acessos = EXCLUDED.health_score_acessos,
    health_score_ces = EXCLUDED.health_score_ces,
    health_score_crescimento_cliente = EXCLUDED.health_score_crescimento_cliente,
    health_score_inadimplencia = EXCLUDED.health_score_inadimplencia,
    health_score_interacao_cliente = EXCLUDED.health_score_interacao_cliente,
    health_score_nota = EXCLUDED.health_score_nota,
    health_score_nps = EXCLUDED.health_score_nps,
    health_score_sem_sentimento = EXCLUDED.health_score_sem_sentimento,
    health_score_sentimento = EXCLUDED.health_score_sentimento,
    health_score_tickets_outros = EXCLUDED.health_score_tickets_outros,
    health_score_tickets_problema = EXCLUDED.health_score_tickets_problema,
    health_score_usa_logmanager = EXCLUDED.health_score_usa_logmanager,
    health_score_usa_logtracking = EXCLUDED.health_score_usa_logtracking,
    health_score_usa_ncm = EXCLUDED.health_score_usa_ncm,
    health_score_usa_shipment = EXCLUDED.health_score_usa_shipment,
    health_score_usabilidade_geral = EXCLUDED.health_score_usabilidade_geral,
    hs_country_code = EXCLUDED.hs_country_code,
    hs_updated_by_user_id = EXCLUDED.hs_updated_by_user_id,
    hubspot_owner_assigneddate = EXCLUDED.hubspot_owner_assigneddate,
    hubspot_owner_id = EXCLUDED.hubspot_owner_id,
    hubspot_team_id = EXCLUDED.hubspot_team_id,
    id_lead = EXCLUDED.id_lead,
    id_logcomex = EXCLUDED.id_logcomex,
    idioma_do_cliente = EXCLUDED.idioma_do_cliente,
    implementador = EXCLUDED.implementador,
    implementador_cross_sell = EXCLUDED.implementador_cross_sell,
    jur_aviso_previo_cancelamento = EXCLUDED.jur_aviso_previo_cancelamento,
    jur_forma_de_renovacao = EXCLUDED.jur_forma_de_renovacao,
    jur_reajuste_anual = EXCLUDED.jur_reajuste_anual,
    jur_rescisao_antecipada_com_multa = EXCLUDED.jur_rescisao_antecipada_com_multa,
    jur_vigencia_do_contrato = EXCLUDED.jur_vigencia_do_contrato,
    mat_area_preparada_para_dado = EXCLUDED.mat_area_preparada_para_dado,
    mat_especializacao_em_comex = EXCLUDED.mat_especializacao_em_comex,
    mat_nivel_utilizacao_de_dado = EXCLUDED.mat_nivel_utilizacao_de_dado,
    mkt_cliente_ativo = EXCLUDED.mkt_cliente_ativo,
    mkt_cliente_internacional = EXCLUDED.mkt_cliente_internacional,
    mkt_cnpj = EXCLUDED.mkt_cnpj,
    mkt_nome_da_empresa = EXCLUDED.mkt_nome_da_empresa,
    mkt_produtos_ativos = EXCLUDED.mkt_produtos_ativos,
    mrr_bu_intelligence = EXCLUDED.mrr_bu_intelligence,
    mrr_bu_operational = EXCLUDED.mrr_bu_operational,
    mrr_r = EXCLUDED.mrr_r,
    numberofemployees = EXCLUDED.numberofemployees,
    ob_aud_auditoria_cliente_e_contrato = EXCLUDED.ob_aud_auditoria_cliente_e_contrato,
    ob_aud_auditoria_engajamento_do_cliente = EXCLUDED.ob_aud_auditoria_engajamento_do_cliente,
    ob_aud_auditoria_insatisfacoes_e_problemas_clonado = EXCLUDED.ob_aud_auditoria_insatisfacoes_e_problemas_clonado,
    ob_aud_auditoria_maturidade_do_cliente = EXCLUDED.ob_aud_auditoria_maturidade_do_cliente,
    ob_aud_auditoria_observacao_red_flags = EXCLUDED.ob_aud_auditoria_observacao_red_flags,
    ob_aud_auditoria_observacao_yellow_flags = EXCLUDED.ob_aud_auditoria_observacao_yellow_flags,
    ob_aud_observacoes_yellow_flag_in = EXCLUDED.ob_aud_observacoes_yellow_flag_in,
    ob_aud_yellow_flags_in_clonado = EXCLUDED.ob_aud_yellow_flags_in_clonado,
    ob_aud_yellow_flags_out_clonado = EXCLUDED.ob_aud_yellow_flags_out_clonado,
    ob_casos_de_uso = EXCLUDED.ob_casos_de_uso,
    ob_data_de_agendamento_clonado = EXCLUDED.ob_data_de_agendamento_clonado,
    ob_data_de_kickoff = EXCLUDED.ob_data_de_kickoff,
    ob_i_classificacao_do_cliente = EXCLUDED.ob_i_classificacao_do_cliente,
    ob_i_cliente_liberado_sem_pgto = EXCLUDED.ob_i_cliente_liberado_sem_pgto,
    ob_i_conclusao_da_implementacao = EXCLUDED.ob_i_conclusao_da_implementacao,
    ob_i_frequencia_de_usabilidade = EXCLUDED.ob_i_frequencia_de_usabilidade,
    ob_i_inicio_da_implementacao = EXCLUDED.ob_i_inicio_da_implementacao,
    ob_i_status_do_onboarding = EXCLUDED.ob_i_status_do_onboarding,
    ob_maturidade_do_cliente = EXCLUDED.ob_maturidade_do_cliente,
    ob_mostrou_risco_de_cancelar = EXCLUDED.ob_mostrou_risco_de_cancelar,
    ob_observacoes_red_flag_cs = EXCLUDED.ob_observacoes_red_flag_cs,
    ob_qtde_de_usuarios = EXCLUDED.ob_qtde_de_usuarios,
    ob_tipo_de_onboarding = EXCLUDED.ob_tipo_de_onboarding,
    obj_a_log_atende_o_objetivo_cs = EXCLUDED.obj_a_log_atende_o_objetivo_cs,
    obj_a_log_esta_contribuindo_cs = EXCLUDED.obj_a_log_esta_contribuindo_cs,
    obj_estrategia_para_objetivo_cs = EXCLUDED.obj_estrategia_para_objetivo_cs,
    obj_nivel_de_atingimento_cs = EXCLUDED.obj_nivel_de_atingimento_cs,
    obj_objetivo_com_o_produto_cs = EXCLUDED.obj_objetivo_com_o_produto_cs,
    obj_satisfacao_atingimento_cs = EXCLUDED.obj_satisfacao_atingimento_cs,
    obj_tem_clareza_no_objetivo = EXCLUDED.obj_tem_clareza_no_objetivo,
    og_cliente_sinalizou_perda = EXCLUDED.og_cliente_sinalizou_perda,
    og_aut_maturidade_do_cliente = EXCLUDED.og_aut_maturidade_do_cliente,
    og_equipe_secundaria = EXCLUDED.og_equipe_secundaria,
    og_reversao_de_perda = EXCLUDED.og_reversao_de_perda,
    og_status_da_aprovacao_desconto_isencao_clonado = EXCLUDED.og_status_da_aprovacao_desconto_isencao_clonado,
    og_valor_revertido = EXCLUDED.og_valor_revertido,
    ops_client_success = EXCLUDED.ops_client_success,
    origem_da_empresa = EXCLUDED.origem_da_empresa,
    pais_menu_suspenso = EXCLUDED.pais_menu_suspenso,
    pais_de_operacao_principal = EXCLUDED.pais_de_operacao_principal,
    passagem_de_bastao_para_cs = EXCLUDED.passagem_de_bastao_para_cs,
    quantidade_de_exportadores = EXCLUDED.quantidade_de_exportadores,
    sales_alteracao_no_plano_padrao = EXCLUDED.sales_alteracao_no_plano_padrao,
    sales_isencao_de_pagamento_carencia = EXCLUDED.sales_isencao_de_pagamento_carencia,
    sales_percentual_de_desconto_no_mrr = EXCLUDED.sales_percentual_de_desconto_no_mrr,
    sales_percentual_desconto_onboarding = EXCLUDED.sales_percentual_desconto_onboarding,
    sales_recuperacao_judicial = EXCLUDED.sales_recuperacao_judicial,
    sales_venda_para_cpf = EXCLUDED.sales_venda_para_cpf,
    score_empresa_inadimplente = EXCLUDED.score_empresa_inadimplente,
    sdr_maturidade_do_cliente = EXCLUDED.sdr_maturidade_do_cliente,
    state = EXCLUDED.state,
    sv_acoes_para_reversao = EXCLUDED.sv_acoes_para_reversao,
    tipo_de_pagamento_frequencia = EXCLUDED.tipo_de_pagamento_frequencia,
    user_guardiao = EXCLUDED.user_guardiao,
    user_guardiao_secundario = EXCLUDED.user_guardiao_secundario,
    user_quality = EXCLUDED.user_quality,
    valor_cif = EXCLUDED.valor_cif,
    website = EXCLUDED.website,
    zip = EXCLUDED.zip
  RETURNING hs_object_id INTO result_id;
  
  RETURN result_id;
END;
$function$
;

-- DROP FUNCTION public.vector(vector, int4, bool);

CREATE OR REPLACE FUNCTION public.vector(vector, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector$function$
;

-- DROP FUNCTION public.vector_accum(_float8, vector);

CREATE OR REPLACE FUNCTION public.vector_accum(double precision[], vector)
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_accum$function$
;

-- DROP FUNCTION public.vector_add(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_add(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_add$function$
;

-- DROP FUNCTION public.vector_avg(_float8);

CREATE OR REPLACE FUNCTION public.vector_avg(double precision[])
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_avg$function$
;

-- DROP FUNCTION public.vector_cmp(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_cmp(vector, vector)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_cmp$function$
;

-- DROP FUNCTION public.vector_combine(_float8, _float8);

CREATE OR REPLACE FUNCTION public.vector_combine(double precision[], double precision[])
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_combine$function$
;

-- DROP FUNCTION public.vector_concat(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_concat(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_concat$function$
;

-- DROP FUNCTION public.vector_dims(vector);

CREATE OR REPLACE FUNCTION public.vector_dims(vector)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_dims$function$
;

-- DROP FUNCTION public.vector_dims(halfvec);

CREATE OR REPLACE FUNCTION public.vector_dims(halfvec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_vector_dims$function$
;

-- DROP FUNCTION public.vector_eq(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_eq(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_eq$function$
;

-- DROP FUNCTION public.vector_ge(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_ge(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_ge$function$
;

-- DROP FUNCTION public.vector_gt(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_gt(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_gt$function$
;

-- DROP FUNCTION public.vector_in(cstring, oid, int4);

CREATE OR REPLACE FUNCTION public.vector_in(cstring, oid, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_in$function$
;

-- DROP FUNCTION public.vector_l2_squared_distance(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_l2_squared_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_l2_squared_distance$function$
;

-- DROP FUNCTION public.vector_le(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_le(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_le$function$
;

-- DROP FUNCTION public.vector_lt(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_lt(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_lt$function$
;

-- DROP FUNCTION public.vector_mul(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_mul(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_mul$function$
;

-- DROP FUNCTION public.vector_ne(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_ne(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_ne$function$
;

-- DROP FUNCTION public.vector_negative_inner_product(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_negative_inner_product(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_negative_inner_product$function$
;

-- DROP FUNCTION public.vector_norm(vector);

CREATE OR REPLACE FUNCTION public.vector_norm(vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_norm$function$
;

-- DROP FUNCTION public.vector_out(vector);

CREATE OR REPLACE FUNCTION public.vector_out(vector)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_out$function$
;

-- DROP FUNCTION public.vector_recv(internal, oid, int4);

CREATE OR REPLACE FUNCTION public.vector_recv(internal, oid, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_recv$function$
;

-- DROP FUNCTION public.vector_send(vector);

CREATE OR REPLACE FUNCTION public.vector_send(vector)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_send$function$
;

-- DROP FUNCTION public.vector_spherical_distance(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_spherical_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_spherical_distance$function$
;

-- DROP FUNCTION public.vector_sub(vector, vector);

CREATE OR REPLACE FUNCTION public.vector_sub(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_sub$function$
;

-- DROP FUNCTION public.vector_to_float4(vector, int4, bool);

CREATE OR REPLACE FUNCTION public.vector_to_float4(vector, integer, boolean)
 RETURNS real[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_float4$function$
;

-- DROP FUNCTION public.vector_to_halfvec(vector, int4, bool);

CREATE OR REPLACE FUNCTION public.vector_to_halfvec(vector, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_halfvec$function$
;

-- DROP FUNCTION public.vector_to_sparsevec(vector, int4, bool);

CREATE OR REPLACE FUNCTION public.vector_to_sparsevec(vector, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_sparsevec$function$
;

-- DROP FUNCTION public.vector_typmod_in(_cstring);

CREATE OR REPLACE FUNCTION public.vector_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_typmod_in$function$
;