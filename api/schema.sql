CREATE TABLE IF NOT EXISTS public_mails(
    `email_uuid` BIGINT PRIMARY KEY,
    `email_recipient` VARCHAR(255) NOT NULL,
    `sent_timpestamp` DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS opens_at(
    `email_uuid` BIGINT,
    `opened_at` DATETIME NOT NULL,
    FOREIGN KEY(`email_uuid`) REFERENCES public_mails(`email_uuid`)
);