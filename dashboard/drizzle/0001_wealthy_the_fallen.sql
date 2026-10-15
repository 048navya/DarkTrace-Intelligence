CREATE TABLE `anchors` (
	`id` text PRIMARY KEY NOT NULL,
	`evidence_id` text NOT NULL,
	`digest` text NOT NULL,
	`status` text NOT NULL,
	`transaction_id` text,
	`receipt` text,
	`created_at` text NOT NULL,
	`error` text
);
--> statement-breakpoint
CREATE INDEX `anchor_evidence_idx` ON `anchors` (`evidence_id`);--> statement-breakpoint
CREATE TABLE `collection_configs` (
	`source_id` text PRIMARY KEY NOT NULL,
	`url` text NOT NULL,
	`adapter` text NOT NULL,
	`interval_seconds` integer NOT NULL,
	`next_run` text NOT NULL,
	`lease_until` text,
	`lease_token` text,
	`failures` integer DEFAULT 0 NOT NULL,
	`authorization` text NOT NULL,
	`last_error` text,
	`last_heartbeat` text
);
--> statement-breakpoint
CREATE TABLE `entities` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`kind` text NOT NULL,
	`source` text NOT NULL,
	`identifiers` text NOT NULL,
	`created_at` text NOT NULL,
	`synthetic` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE `models` (
	`id` text PRIMARY KEY NOT NULL,
	`created_at` text NOT NULL,
	`content` text NOT NULL,
	`active` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE `observations` (
	`id` text PRIMARY KEY NOT NULL,
	`record_id` text NOT NULL,
	`digest` text NOT NULL,
	`content` text NOT NULL,
	`collected_at` text NOT NULL,
	`source_id` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `observation_record_idx` ON `observations` (`record_id`,`collected_at`);