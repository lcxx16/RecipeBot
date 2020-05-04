CREATE OR REPLACE FUNCTION public.process_backup()
 RETURNS trigger
 LANGUAGE plpgsql
AS 
'
BEGIN 
	INSERT INTO product_archive SELECT OLD.*;
	RETURN OLD;
END
'

CREATE TRIGGER backup_recode 
AFTER DELETE ON product 
 FOR EACH ROW EXECUTE PROCEDURE process_backup();
