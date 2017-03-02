CREATE TABLE `addresses` (
`id` bigint NOT NULL AUTO_INCREMENT,
`street` varchar(128) NULL DEFAULT NULL,
`apt` varchar(256) NULL,
`city` varchar(128) NULL DEFAULT NULL,
`state` varchar(128) NULL DEFAULT NULL,
`zip` varchar(32) NULL,
`country` varchar(128) NULL DEFAULT 'USA',
`sources_id` smallint NOT NULL DEFAULT 1,
`id_from_source` bigint NULL,
`source_table` varchar(32) NULL,
`created_at` datetime NULL,
`updated_at` datetime NULL,
PRIMARY KEY (`id`) ,
INDEX `fk_Addresses_Sources1_idx` (`sources_id` ASC) USING BTREE,
INDEX `address_ind1` (`street` ASC, `city` ASC, `state` ASC, `zip` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `answers` (
`id` bigint NOT NULL,
`question_id` int(11) NULL DEFAULT NULL,
`value` text NULL,
`type` varchar(255) NULL DEFAULT NULL,
`answerable_type` varchar(255) NULL DEFAULT NULL,
`answerable_id` bigint NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_answers_on_answerable_id_and_answerable_type` (`answerable_id` ASC, `answerable_type` ASC, `question_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `businesses` (
`id` bigint NOT NULL AUTO_INCREMENT,
`name` varchar(64) NULL DEFAULT NULL,
`encrypted_tax_id` varchar(128) NULL DEFAULT NULL,
`dln` varchar(16) NULL DEFAULT NULL,
`fiscal_year_end_date` date NULL DEFAULT NULL,
`business_type` varchar(16) NOT NULL,
`no_of_employees` int(11) NULL DEFAULT NULL,
`trade_name` varchar(128) NULL DEFAULT NULL,
`phone` varchar(16) NULL DEFAULT NULL,
`fax` varchar(16) NULL DEFAULT NULL,
`industry_id` bigint NULL,
`sources_id` int(11) NOT NULL,
`id_from_source` bigint NULL,
`source_table` varchar(32) NULL,
`created_at` datetime NULL,
`updated_at` datetime NULL,
PRIMARY KEY (`id`) ,
INDEX `fk_Business_Sources1_idx` (`sources_id` ASC) USING BTREE,
INDEX `business_source_id_source_tab_ind1` (`id_from_source` ASC, `source_table` ASC)
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `decisions` (
`id` bigint NOT NULL,
`loan_id` bigint NULL DEFAULT NULL,
`decision` tinyint(1) NULL DEFAULT NULL,
`request_type` varchar(255) NULL DEFAULT NULL,
`amount` int(11) NULL DEFAULT NULL,
`max_amount` int(11) NULL DEFAULT NULL,
`liquidity_ratio` decimal(11,2) NULL DEFAULT NULL,
`mitigating_factor` tinyint(1) NULL DEFAULT NULL,
`business_score` decimal(11,0) NULL DEFAULT 0,
`minimum_credit_score` decimal(11,0) NULL DEFAULT 0,
`risk_rating` float NULL DEFAULT NULL,
`guarantors_20` int(11) NULL DEFAULT NULL,
`business_type` varchar(255) NULL DEFAULT NULL,
`smart_rate` int(11) NULL DEFAULT NULL,
`smart_rate_v2` int(11) NULL DEFAULT NULL,
`risk_rating_v2` float NULL DEFAULT NULL,
`risk_rating_data` text NULL,
`lender_id` int(11) NULL DEFAULT NULL,
`liquid_credit_id` int(11) NULL DEFAULT NULL,
`product_id` int(11) NOT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_decisions_on_loan_id` (`loan_id` ASC) USING BTREE,
INDEX `index_decisions_on_risk_rating` (`risk_rating` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `etrans` (
`id` bigint NOT NULL,
`loan_id` bigint NULL DEFAULT NULL,
`score` int(11) NULL DEFAULT NULL,
`app_number` decimal(12,0) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_etrans_on_loan_id` (`loan_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `financial_adjustments` (
`id` bigint NOT NULL,
`category` varchar(64) NULL DEFAULT NULL,
`reason` text NULL,
`adjustable_type` varchar(64) NULL DEFAULT NULL,
`adjustable_id` int(11) NULL DEFAULT NULL,
`description` varchar(255) NULL DEFAULT NULL,
`data` text NULL,
`type` varchar(64) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_financial_adjustments_on_adjustable_id` (`adjustable_id` ASC) USING BTREE,
INDEX `index_financial_adjustments_on_adjustable_type` (`adjustable_type` ASC) USING BTREE,
INDEX `index_financial_adjustments_on_adjustable_id_and_adjustable_type` (`adjustable_id` ASC, `adjustable_type` ASC) USING BTREE,
INDEX `index_financial_adjustments_on_type` (`type` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `financials` (
`id` bigint NOT NULL,
`loan_id` bigint NULL DEFAULT NULL,
`bank_account` varchar(255) NULL DEFAULT NULL,
`routing_number` varchar(255) NULL DEFAULT NULL,
`integration` tinyint(1) NULL DEFAULT NULL,
`open` tinyint(1) NULL DEFAULT 1,
`confirmed` tinyint(1) NULL DEFAULT 0,
`encrypted_account_number` varchar(255) NULL DEFAULT NULL,
`personal_average_balance` tinyint(1) NULL DEFAULT 0,
`average_balance_based_on` date NULL DEFAULT NULL,
`fiscal_year_end_on` date NULL DEFAULT NULL,
`last_tax_return_on` date NULL DEFAULT NULL,
`skip_bank_account` tinyint(1) NULL DEFAULT 0,
`business_id` bigint NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_financials_on_loan_id` (`loan_id` ASC) USING BTREE,
INDEX `index_financials_on_business_id` (`business_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `income_statements` (
`id` bigint NOT NULL,
`financial_id` bigint NULL DEFAULT NULL,
`gross_sales` decimal(11,2) NULL DEFAULT NULL,
`interest_expense` decimal(11,2) NULL DEFAULT NULL,
`depreciation_expense` decimal(11,2) NULL DEFAULT NULL,
`net_income` decimal(11,2) NULL DEFAULT NULL,
`total_expenses` decimal(11,2) NULL DEFAULT NULL,
`income_statement_from` date NULL DEFAULT NULL,
`income_statement_to` date NULL DEFAULT NULL,
`cogs` decimal(11,2) NULL DEFAULT NULL,
`officers_compensation` decimal(11,2) NULL DEFAULT NULL,
`business_property_rental_expense` decimal(11,2) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_income_statements_on_financial_id` (`financial_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `industries` (
`id` int(11) NOT NULL,
`code` int(11) NULL DEFAULT NULL,
`title` varchar(255) NULL DEFAULT NULL,
`parent_id` int(11) NULL DEFAULT NULL,
`eligible` tinyint(1) NULL DEFAULT 1,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_industries_on_parent_id` (`parent_id` ASC) USING BTREE,
INDEX `index_industries_on_code` (`code` ASC) USING BTREE,
INDEX `index_industries_on_title` (`title` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `lenders` (
`id` int(11) NOT NULL,
`name` varchar(64) NULL DEFAULT NULL,
`name_short` varchar(32) NULL DEFAULT NULL,
`address_id` bigint(11) NULL,
`contact_first_name` varchar(32) NULL,
`contact_last_name` varchar(32) NULL,
`contact_phone` varchar(16) NULL,
`contact_fax` varchar(16) NULL,
`identifier` varchar(255) NULL DEFAULT NULL,
`type` varchar(32) NULL DEFAULT NULL,
`manual_max` decimal(11,2) NULL DEFAULT NULL,
`manual_min` decimal(11,2) NULL DEFAULT NULL,
`credit_score_provider` int(11) NOT NULL DEFAULT 0,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) 
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `liquid_credits` (
`id` bigint NOT NULL,
`loan_id` bigint NULL DEFAULT NULL,
`encrypted_json_response` longtext NULL,
`encrypted_lender_json_response` longtext NULL,
`mocked` tinyint(1) NULL DEFAULT NULL,
`pull_type` varchar(255) NULL DEFAULT NULL,
`version` varchar(255) NULL DEFAULT NULL,
`submission_id` varchar(255) NULL DEFAULT NULL,
`lender_id` bigint NULL DEFAULT NULL,
`copy` tinyint(1) NULL DEFAULT 0,
`credit_issue` tinyint(1) NULL DEFAULT NULL,
`public_record_issue` tinyint(1) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_liquid_credits_on_loan_id` (`loan_id` ASC) USING BTREE,
INDEX `index_liquid_credits_on_lender_id` (`lender_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `loans` (
`id` bigint NOT NULL AUTO_INCREMENT,
`loan_id` bigint NULL,
`person_id` int(11) NULL DEFAULT NULL,
`amount` int(11) NULL DEFAULT NULL,
`term` int(11) NULL DEFAULT NULL,
`interest_rate` decimal(9,3) NULL DEFAULT NULL,
`prime_rate` decimal(9,3) NULL DEFAULT NULL,
`monthly_payment` decimal(11,2) NULL DEFAULT NULL,
`fees` decimal(11,2) NULL DEFAULT NULL,
`interest_rate_with_fees` decimal(9,3) NULL DEFAULT NULL,
`state` varchar(255) NULL DEFAULT NULL,
`campaign_id` varchar(255) NULL DEFAULT NULL,
`admin_id` int(11) NULL DEFAULT NULL,
`max_loan_amount_clean` int(11) NULL DEFAULT NULL,
`amount_requested` int(11) NULL DEFAULT NULL,
`promo_code` varchar(255) NULL DEFAULT NULL,
`lender_id` int(11) NULL DEFAULT NULL,
`sales_assisted` tinyint(1) NULL DEFAULT NULL,
`api_assisted` tinyint(1) NULL DEFAULT 0,
`external_member_status` varchar(255) NULL DEFAULT NULL,
`partner_id` int(11) NULL DEFAULT NULL,
`promotion_id` int(11) NULL DEFAULT NULL,
`handed_off_at` datetime NULL DEFAULT NULL,
`partner_referral_pct` float NULL DEFAULT 0,
`lead_id` int(11) NULL DEFAULT NULL,
`referred_by_id` int(11) NULL DEFAULT NULL,
`partner_customer_id` varchar(255) NULL DEFAULT NULL,
`sales_assisted_requested_at` datetime NULL DEFAULT NULL,
`sales_assisted_denied_at` datetime NULL DEFAULT NULL,
`assigned_date` datetime NULL DEFAULT NULL,
`assignment_read_at` datetime NULL DEFAULT NULL,
`active_items` text NULL,
`intended_use_of_funds` varchar(255) NULL DEFAULT NULL,
`recommended_apply_date` date NULL DEFAULT NULL,
`agency` varchar(255) NULL DEFAULT NULL,
`source` varchar(255) NULL DEFAULT NULL,
`medium` varchar(255) NULL DEFAULT NULL,
`reengagement` int(11) NULL DEFAULT NULL,
`priority` int(11) NULL DEFAULT NULL,
`position` int(11) NULL DEFAULT NULL,
`fees_hash` text NULL,
`product_id` int(11) NULL DEFAULT NULL,
`previous_state` varchar(255) NULL DEFAULT NULL,
`last_statistic_created_at` datetime NULL DEFAULT NULL,
`smart_rate` int(11) NULL DEFAULT NULL,
`rec_status` tinyint NULL DEFAULT 1,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `loans_loan_id_indx` (`loan_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `loans_reasons` (
`id` bigint NOT NULL,
`loan_id` int(11) NULL DEFAULT NULL,
`reason_id` int(11) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) 
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `partners` (
`id` bigint NOT NULL,
`name` varchar(255) NULL DEFAULT NULL,
`display_name` varchar(255) NULL DEFAULT '',
`lender_id` bigint NULL DEFAULT NULL,
`loan_term` int(11) NULL DEFAULT NULL,
`prepayment_penalty` text NULL,
`primary_type` int(11) NULL DEFAULT NULL,
`referral_pct` float NULL DEFAULT 0,
`state_updated_at` datetime NULL DEFAULT NULL,
`smartrate` tinyint(1) NULL DEFAULT 0,
`owner_id` int(11) NULL DEFAULT NULL,
`special_partner` tinyint(1) NULL DEFAULT 0,
`aggregator_partner` tinyint(1) NULL DEFAULT 0,
`partner_assisted` tinyint(1) NULL DEFAULT 1,
`min_smart_rate` int(11) NULL DEFAULT 0,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_partners_on_name` (`name` ASC) USING BTREE,
INDEX `index_partners_on_lender_id` (`lender_id` ASC) USING BTREE,
INDEX `index_partners_on_owner_id` (`owner_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `persons` (
`id` bigint NOT NULL AUTO_INCREMENT,
`first_name` varchar(64) NULL DEFAULT NULL,
`middle_name` varchar(64) NULL DEFAULT NULL,
`last_name` varchar(64) NULL DEFAULT NULL,
`person_type` varchar(16) NOT NULL,
`sources_id` bigint NOT NULL,
`gender` varchar(45) NULL DEFAULT NULL,
`DOB` datetime NULL,
`email` varchar(64) NULL DEFAULT NULL,
`phone` varchar(16) NULL DEFAULT NULL,
`mobile_phone` varchar(16) NULL DEFAULT NULL,
`fax` varchar(16) NULL,
`citizenship` varchar(32) NULL DEFAULT NULL,
`admin` tinyint(1) NULL DEFAULT NULL,
`id_from_source` bigint NULL DEFAULT NULL,
`source_table` varchar(32) NULL,
`created_at` datetime NULL,
`updated_at` datetime NULL,
PRIMARY KEY (`id`) ,
INDEX `fk_Business_Persons_Sources1_idx` (`sources_id` ASC) USING BTREE,
INDEX `person_id_from_source_ind1` (`id_from_source` ASC, `source_table` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `products` (
`id` int(11) NOT NULL,
`lender_id` int(11) NULL DEFAULT NULL,
`name` varchar(255) NULL DEFAULT NULL,
`info` text NULL,
`category` int(11) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_products_on_lender_id` (`lender_id` ASC) USING BTREE,
INDEX `index_products_on_name` (`name` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `promotions` (
`id` bigint NOT NULL,
`name` varchar(255) NULL DEFAULT NULL,
`partner_id` bigint NULL DEFAULT NULL,
`starts_at` datetime NULL DEFAULT NULL,
`ends_at` datetime NULL DEFAULT NULL,
`active` tinyint(1) NULL DEFAULT NULL,
`default` tinyint(1) NULL DEFAULT NULL,
`description` varchar(255) NULL DEFAULT NULL,
`lender_id` bigint NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_promotions_on_partner_id` (`partner_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `questions` (
`id` int(11) NOT NULL,
`section` varchar(255) NULL DEFAULT NULL,
`description` text NULL,
`format` varchar(255) NULL DEFAULT NULL,
`parent_id` int(11) NULL DEFAULT NULL,
`number` int(11) NULL DEFAULT NULL,
`required_answer` varchar(255) NULL DEFAULT NULL,
`active` tinyint(1) NULL DEFAULT 1,
`parent_answer` varchar(255) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_questions_on_parent_id` (`parent_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `reasons` (
`id` int(11) NOT NULL,
`code` varchar(255) NULL DEFAULT NULL,
`description` varchar(255) NULL DEFAULT NULL,
`manual` varchar(255) NULL DEFAULT NULL,
`type` varchar(255) NULL DEFAULT NULL,
`created_at` datetime NULL,
`updated_at` datetime NULL,
PRIMARY KEY (`id`) ,
INDEX `index_reasons_on_type` (`type` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `sources` (
`id` smallint(11) NOT NULL AUTO_INCREMENT,
`name` varchar(64) NOT NULL,
`active` varchar(3) NOT NULL,
`created_at` datetime NULL,
`updated_at` datetime NULL,
PRIMARY KEY (`id`) 
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `statistics` (
`id` bigint NOT NULL,
`loan_id` bigint NULL DEFAULT NULL,
`state` varchar(255) NULL DEFAULT NULL,
`lender_id` int(11) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `index_statistics_on_loan_id` (`loan_id` ASC) USING BTREE,
INDEX `index_statistics_on_state` (`state` ASC) USING BTREE,
INDEX `index_statistics_on_created_at` (`created_at` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `tax_items` (
`id` bigint NOT NULL AUTO_INCREMENT,
`item` varchar(128) NULL DEFAULT NULL,
`item_type` varchar(16) NULL DEFAULT NULL,
`needed_for_dw` tinyint(1) NULL DEFAULT 0,
PRIMARY KEY (`id`) ,
UNIQUE INDEX `id_UNIQUE` (`id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `tax_return_items` (
`id` bigint NOT NULL AUTO_INCREMENT,
`tax_item_id` bigint NOT NULL,
`item_value` varchar(45) NULL DEFAULT NULL,
`tax_returns_id` bigint(20) NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `fk_Tax_Return_Items_Tax_Items1_idx` (`tax_item_id` ASC) USING BTREE,
INDEX `fk_Tax_Return_Items_Tax_Returns1_idx` (`tax_returns_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `tax_returns` (
`id` bigint NOT NULL AUTO_INCREMENT,
`year` int(11) NULL DEFAULT NULL,
`form_type` varchar(16) NULL DEFAULT NULL,
`filing_status` varchar(45) NULL DEFAULT NULL,
`processing_date` date NULL DEFAULT NULL,
`social_bp_Id` bigint NOT NULL,
`co_social_bp_id` bigint NOT NULL,
`business_id` bigint NOT NULL,
PRIMARY KEY (`id`) ,
INDEX `fk_Tax_Returns_Business_Persons1_idx` (`social_bp_Id` ASC) USING BTREE,
INDEX `fk_Tax_Returns_Business_Persons2_idx` (`co_social_bp_id` ASC) USING BTREE,
INDEX `fk_Tax_Returns_Business1_idx` (`business_id` ASC) USING BTREE
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `use_of_funds` (
`id` bigint NOT NULL,
`verification_id` int(11) NULL DEFAULT NULL,
`business_expansion` decimal(11,2) NULL DEFAULT 0.00,
`inventory` decimal(11,2) NULL DEFAULT 0.00,
`hiring` decimal(11,2) NULL DEFAULT 0.00,
`marketing` decimal(11,2) NULL DEFAULT 0.00,
`operational_costs` decimal(11,2) NULL DEFAULT 0.00,
`new_equipment` decimal(11,2) NULL DEFAULT 0.00,
`other` decimal(11,2) NULL DEFAULT 0.00,
`other_description` text NULL,
`total` decimal(11,2) NULL DEFAULT NULL,
`confirmed` tinyint(1) NULL DEFAULT 0,
`refinance` decimal(11,2) NULL DEFAULT 0.00,
`real_estate_mortgage_refinance` decimal(11,2) NULL DEFAULT 0.00,
`real_estate_purchase` decimal(11,2) NULL DEFAULT 0.00,
`business_acquisition` decimal(11,2) NULL DEFAULT 0.00,
`commercial_real_estate_loan` decimal(11,2) NULL DEFAULT 0.00,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
PRIMARY KEY (`id`) 
)
ENGINE = InnoDB
ROW_FORMAT = compact;

CREATE TABLE `person_business_addresses` (
`id` bigint NOT NULL AUTO_INCREMENT,
`address_id` bigint NULL,
`addressable_type` varchar(32) NULL COMMENT 'Business, Guarantor, TaxReturnPersonal, RealEstate',
`business_person_id` bigint NULL,
`address_type` varchar(32) NULL COMMENT 'Primary, Secondary, Tax, Mailing, Property',
`active` tinyint NOT NULL DEFAULT 1,
PRIMARY KEY (`id`) ,
INDEX `pers_bus_pid_addrid_ind` (`business_person_id` ASC, `addressable_type` ASC, `address_id` ASC)
);

CREATE TABLE `loan_business_info` (
`id` bigint NOT NULL AUTO_INCREMENT,
`business_id` bigint NULL,
`loan_id` bigint NULL,
PRIMARY KEY (`id`) 
);

CREATE TABLE `dw_processes_info` (
`id` bigint NOT NULL AUTO_INCREMENT,
`process_name` varchar(32) NOT NULL,
`last_process_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`) 
);

CREATE TABLE `verifications` (
`id` int(11) NOT NULL AUTO_INCREMENT,
`loan_id` int(11) NULL DEFAULT NULL,
`created_at` datetime NOT NULL,
`updated_at` datetime NOT NULL,
`credit_pull_permitted` tinyint(1) NULL DEFAULT 0,
PRIMARY KEY (`id`) 
)
ENGINE = InnoDB
ROW_FORMAT = compact;

