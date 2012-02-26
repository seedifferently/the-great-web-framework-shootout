<?

class Model_Hello extends Orm\Model {
    public static $_table_name = 'hello';
	
	 protected static $_properties = array(
        'id',
        'data',
        );
}