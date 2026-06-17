-- MySQL schema (run inside database selected by code)

CREATE TABLE IF NOT EXISTS `user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(255) NULL,
  `phone` VARCHAR(20) NULL,
  `role` VARCHAR(32) NULL DEFAULT 'staff',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_username` (`username`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `vehicle` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `plate_number` VARCHAR(32) NOT NULL,
  `vehicle_type` VARCHAR(32) NULL DEFAULT 'car',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_vehicle_plate_number` (`plate_number`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `parking_zones` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `zone_name` VARCHAR(64) NOT NULL,
  `vehicle_type` VARCHAR(32) NOT NULL DEFAULT 'all',
  `capacity` INT NOT NULL DEFAULT 0,
  `active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_parking_zones_name` (`zone_name`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `parking_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `vehicle_id` INT NOT NULL,
  `user_id` INT NULL,
  `zone_id` INT NULL,
  `entry_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `exit_time` DATETIME NULL,
  `status` VARCHAR(8) NULL DEFAULT 'in',
  `note` TEXT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parking_records_vehicle_status` (`vehicle_id`, `status`),
  CONSTRAINT `fk_parking_records_vehicle`
    FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle` (`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_parking_records_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_parking_records_zone`
    FOREIGN KEY (`zone_id`) REFERENCES `parking_zones` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `images` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `parking_record_id` INT NOT NULL,
  `image_path` VARCHAR(1024) NOT NULL,
  `image_type` VARCHAR(16) NOT NULL,
  `plate_detected` VARCHAR(32) NULL,
  `confidence` DOUBLE NULL,
  `captured_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_images_parking_record` (`parking_record_id`),
  CONSTRAINT `fk_images_parking_record`
    FOREIGN KEY (`parking_record_id`) REFERENCES `parking_records` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `fee_rules` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `vehicle_type` VARCHAR(32) NOT NULL,
  `first_block_minutes` INT NOT NULL DEFAULT 60,
  `first_block_price` DECIMAL(12,2) NOT NULL DEFAULT 0,
  `next_hour_price` DECIMAL(12,2) NOT NULL DEFAULT 0,
  `daily_max_price` DECIMAL(12,2) NULL,
  `active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fee_rules_vehicle_active` (`vehicle_type`, `active`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `payments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `parking_record_id` INT NOT NULL,
  `amount` DECIMAL(12,2) NOT NULL DEFAULT 0,
  `duration_minutes` INT NOT NULL DEFAULT 0,
  `payment_method` VARCHAR(32) NOT NULL DEFAULT 'cash',
  `status` VARCHAR(16) NOT NULL DEFAULT 'paid',
  `paid_by` INT NULL,
  `paid_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payments_parking_record` (`parking_record_id`),
  KEY `idx_payments_paid_by` (`paid_by`),
  CONSTRAINT `fk_payments_parking_record`
    FOREIGN KEY (`parking_record_id`) REFERENCES `parking_records` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_paid_by`
    FOREIGN KEY (`paid_by`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

INSERT INTO `user` (`username`, `password`, `full_name`, `role`)
VALUES ('admin', 'admin123', 'Quan tri vien', 'admin')
ON DUPLICATE KEY UPDATE `username` = `username`;

INSERT INTO `fee_rules`
  (`vehicle_type`, `first_block_minutes`, `first_block_price`, `next_hour_price`, `daily_max_price`, `active`)
VALUES
  ('motorbike', 60, 5000, 3000, 30000, 1),
  ('car', 60, 20000, 10000, 150000, 1)
ON DUPLICATE KEY UPDATE `vehicle_type` = `vehicle_type`;

INSERT INTO `parking_zones` (`zone_name`, `vehicle_type`, `capacity`, `active`)
VALUES
  ('Khu A - Xe may', 'motorbike', 50, 1),
  ('Khu B - O to', 'car', 20, 1)
ON DUPLICATE KEY UPDATE `zone_name` = `zone_name`;
