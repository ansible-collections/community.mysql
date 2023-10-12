DELIMITER //
DROP PROCEDURE IF EXISTS user_accounts_db.get_all_items;
CREATE PROCEDURE user_accounts_db.get_all_items()
BEGIN
SELECT * from user_accounts_db.t1;
END //
DELIMITER ;
