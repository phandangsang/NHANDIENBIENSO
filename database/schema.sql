-- MySQL schema (run inside database selected by code)

CREATE TABLE IF NOT EXISTS `user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(255) NULL,
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

CREATE TABLE IF NOT EXISTS `parking_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `vehicle_id` INT NOT NULL,
  `user_id` INT NULL,
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

INSERT INTO `user` (`username`, `password`, `full_name`, `role`)
VALUES ('admin', 'admin123', 'Quan tri vien', 'admin')
ON DUPLICATE KEY UPDATE `username` = `username`;

ALTER TABLE `user`
ADD COLUMN `online` TINYINT(1) DEFAULT 0,
ADD COLUMN `last_seen` DATETIME NULL,
ADD COLUMN `notif` INT DEFAULT 0;
