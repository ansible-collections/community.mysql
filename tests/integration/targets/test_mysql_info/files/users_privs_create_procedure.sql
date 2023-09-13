DELIMITER //
DROP PROCEDURE IF EXISTS users_privs_db.get_all_items;
CREATE PROCEDURE users_privs_db.get_all_items()
BEGIN
SELECT * from users_privs_db.t1;
END //
DELIMITER ;
