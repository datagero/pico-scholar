CREATE TABLE IF NOT EXISTS `Project` (
  `projectId` VARCHAR(255) PRIMARY KEY,
  `name` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `Users` (
  `userId` VARCHAR(255) PRIMARY KEY,
  `userName` VARCHAR(255),
  `userEmail` VARCHAR(255),
  `createdAt` DATETIME,
  `updatedAt` DATETIME
);

CREATE TABLE IF NOT EXISTS `AcademicDatabases` (
  `databaseId` VARCHAR(255) PRIMARY KEY,
  `databaseName` VARCHAR(255),
  `description` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `Document` (
  `documentId` VARCHAR(255) PRIMARY KEY,
  `title` VARCHAR(255),
  `author` VARCHAR(255),
  `year` INT
);

CREATE TABLE IF NOT EXISTS `DocumentDatabaseMapping` (
  `hashKey` BIGINT PRIMARY KEY,
  `documentId` VARCHAR(255),
  `databaseId` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `DocumentAbstract` (
  `documentId` VARCHAR(255) PRIMARY KEY,
  `abstract` LONGTEXT
);

CREATE TABLE IF NOT EXISTS `DocumentPICO_raw` (
  `documentId` VARCHAR(255) PRIMARY KEY,
  `pico_p` VARCHAR(255),
  `pico_i` VARCHAR(255),
  `pico_c` VARCHAR(255),
  `pico_o` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `DocumentPICO_enhanced` (
  `documentId` VARCHAR(255) PRIMARY KEY,
  `pico_p` VARCHAR(255),
  `pico_i` VARCHAR(255),
  `pico_c` VARCHAR(255),
  `pico_o` VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS `DocumentFull` (
  `documentId` VARCHAR(255) PRIMARY KEY,
  `pdfBlob` LONGBLOB
);


CREATE TABLE IF NOT EXISTS `SearchQueryHistory` (
  `queryId` VARCHAR(255) PRIMARY KEY,
  `projectId` VARCHAR(255),
  `query` TEXT,
  `timestamp` DATETIME
);

CREATE TABLE IF NOT EXISTS `SearchResult` (
  `hashKey` BIGINT PRIMARY KEY,
  `queryId` VARCHAR(255),
  `documentId` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `FunnelStatus` (
  `hashKey` BIGINT PRIMARY KEY,
  `projectId` VARCHAR(255),
  `documentId` VARCHAR(255),
  `status` VARCHAR(255),
  `reviewed` BOOLEAN,
  `effectiveStartDate` DATETIME,
  `effectiveEndDate` DATETIME,
  `isCurrent` BOOLEAN,
  `modifiedBy` VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS `DocumentChatInteraction` (
  `hashKey` BIGINT PRIMARY KEY,
  `sessionId` VARCHAR(255),
  `chatId` VARCHAR(255),
  `userId` VARCHAR(255),
  `documentId` VARCHAR(255),
  `question` TEXT,
  `response` LONGTEXT,
  `timestamp` DATETIME
);

CREATE TABLE IF NOT EXISTS `ProjectFunnelStatistics` (
  `projectQueryId` VARCHAR(255) PRIMARY KEY,
  `projectId` VARCHAR(255),
  `queryId` VARCHAR(255),
  `totalDocuments` INT,
  `identifiedCount` INT,
  `screenedCount` INT,
  `retrievalCount` INT,
  `eligibilityCount` INT,
  `includeCount` INT,
  `excludedCount` INT,
  `pendingCount` INT,
  `lastUpdate` DATETIME
);

-- Indexes
CREATE INDEX `Document_index` ON `Document` (`documentId`);
CREATE UNIQUE INDEX `DocumentDatabaseMapping_index` ON `DocumentDatabaseMapping` (`documentId`, `databaseId`);
CREATE UNIQUE INDEX `SearchResult_index` ON `SearchResult` (`queryId`, `documentId`);
CREATE UNIQUE INDEX `FunnelStatus_index` ON `FunnelStatus` (`projectId`, `documentId`);
CREATE INDEX `DocumentChatInteraction_index` ON `DocumentChatInteraction` (`sessionId`, `chatId`);
CREATE INDEX `ProjectFunnelStatistics_index` ON `ProjectFunnelStatistics` (`projectId`, `queryId`);

-- Foreign keys
ALTER TABLE `SearchQueryHistory` ADD FOREIGN KEY (`projectId`) REFERENCES `Project` (`projectId`);
ALTER TABLE `SearchResult` ADD FOREIGN KEY (`queryId`) REFERENCES `SearchQueryHistory` (`queryId`);
ALTER TABLE `SearchResult` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentAbstract` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentPICO_raw` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentPICO` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentFull` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentDatabaseMapping` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentDatabaseMapping` ADD FOREIGN KEY (`databaseId`) REFERENCES `AcademicDatabases` (`databaseId`);
ALTER TABLE `FunnelStatus` ADD FOREIGN KEY (`projectId`) REFERENCES `Project` (`projectId`);
ALTER TABLE `FunnelStatus` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `FunnelStatus` ADD FOREIGN KEY (`modifiedBy`) REFERENCES `Users` (`userId`);
ALTER TABLE `DocumentChatInteraction` ADD FOREIGN KEY (`documentId`) REFERENCES `Document` (`documentId`);
ALTER TABLE `DocumentChatInteraction` ADD FOREIGN KEY (`userId`) REFERENCES `Users` (`userId`);
