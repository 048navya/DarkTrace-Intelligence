CREATE TABLE `audit` (
	`id` text PRIMARY KEY NOT NULL,
	`action` text NOT NULL,
	`detail` text NOT NULL,
	`created_at` text NOT NULL,
	`author` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `records` (
	`id` text PRIMARY KEY NOT NULL,
	`source_id` text NOT NULL,
	`handle` text NOT NULL,
	`platform` text NOT NULL,
	`category` text NOT NULL,
	`observed_at` text NOT NULL,
	`collected_at` text NOT NULL,
	`last_scan` text NOT NULL,
	`content` text NOT NULL,
	`digest` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `records_observed_idx` ON `records` (`observed_at`);--> statement-breakpoint
CREATE INDEX `records_source_idx` ON `records` (`source_id`);--> statement-breakpoint
CREATE TABLE `reviews` (
	`id` text PRIMARY KEY NOT NULL,
	`relationship_id` text NOT NULL,
	`decision` text NOT NULL,
	`reason` text NOT NULL,
	`created_at` text NOT NULL,
	`author` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `reviews_relation_idx` ON `reviews` (`relationship_id`,`created_at`);--> statement-breakpoint
CREATE TABLE `scans` (
	`id` text PRIMARY KEY NOT NULL,
	`source_id` text NOT NULL,
	`started_at` text NOT NULL,
	`finished_at` text,
	`status` text NOT NULL,
	`count` integer DEFAULT 0 NOT NULL,
	`message` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `sources` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`kind` text NOT NULL,
	`reliability` text NOT NULL,
	`last_scan` text,
	`enabled` integer DEFAULT 1 NOT NULL
);
