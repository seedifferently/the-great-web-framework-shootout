<?php
/**
 * SQLite layer for DBO.
 *
 * PHP versions 4 and 5
 *
 * CakePHP(tm) : Rapid Development Framework (http://cakephp.org)
 * Copyright 2005-2009, Cake Software Foundation, Inc. (http://cakefoundation.org)
 *
 * Licensed under The MIT License
 * Redistributions of files must retain the above copyright notice.
 *
 * @copyright     Copyright 2005-2009, Cake Software Foundation, Inc. (http://cakefoundation.org)
 * @link          http://cakephp.org CakePHP(tm) Project
 * @package       datasources
 * @subpackage    datasources.models.datasources.dbo
 * @since         CakePHP Datasources v 0.1
 * @license       MIT License (http://www.opensource.org/licenses/mit-license.php)
 */

App::import('Datasource','DboSource');

/**
 * DBO implementation for the SQLite3 DBMS.
 *
 * A DboSource adapter for SQLite 3 using PDO
 *
 * @package datasources
 * @subpackage datasources.models.datasources.dbo
 */
class DboSqlite3 extends DboSource {

/**
 * Datasource Description
 *
 * @var string
 * @access public
 */
	var $description = "SQLite3 DBO Driver";

/**
 * Quote Start
 *
 * @var string
 * @access public
 */
	var $startQuote = '"';

/**
 * Quote End
 *
 * @var string
 * @access public
 */
	var $endQuote = '"';

/**
 * Base configuration settings for SQLite3 driver
 *
 * @var array
 * @access public
 */
	var $_baseConfig = array(
		'persistent' => false,
		'database' => null,
		'connect' => 'sqlite' //sqlite3 in pdo_sqlite is sqlite. sqlite2 is sqlite2
	);

/**
 * SQLite3 column definition
 *
 * @var array
 * @access public
 */
	var $columns = array(
		'primary_key' => array('name' => 'integer primary key autoincrement'),
		'string' => array('name' => 'varchar', 'limit' => '255'),
		'text' => array('name' => 'text'),
		'integer' => array('name' => 'integer', 'limit' => null, 'formatter' => 'intval'),
		'float' => array('name' => 'float', 'formatter' => 'floatval'),
		'datetime' => array('name' => 'datetime', 'format' => 'Y-m-d H:i:s', 'formatter' => 'date'),
		'timestamp' => array('name' => 'timestamp', 'format' => 'Y-m-d H:i:s', 'formatter' => 'date'),
		'time' => array('name' => 'time', 'format' => 'H:i:s', 'formatter' => 'date'),
		'date' => array('name' => 'date', 'format' => 'Y-m-d', 'formatter' => 'date'),
		'binary' => array('name' => 'blob'),
		'boolean' => array('name' => 'boolean')
	);

/**
 * List of engine specific additional field parameters used on table creating
 *
 * @var array
 * @access public
 */
	var $fieldParameters = array(
		'collate' => array(
			'value' => 'COLLATE',
			'quote' => false,
			'join' => ' ',
			'column' => 'Collate',
			'position' => 'afterDefault',
			'options' => array(
				'BINARY', 'NOCASE', 'RTRIM'
			)
		),
	);

/**
 * Last Error
 *
 * @var string
 * @access public
 */
	var $last_error = NULL;

/**
 * PDO Statement
 *
 * @var string
 * @access public
 */
	var $pdo_statement = NULL;

/**
 * Rows
 *
 * @var mixed
 * @access public
 */
	var $rows = NULL;

/**
 * Row Count
 *
 * @var integer
 * @access public
 */
	var $row_count = NULL;

/**
 * Transaction Started
 *
 * @var boolean
 * @access protected
 */
	var $_transactionStarted = false;

/**
 * Transaction Nesting
 *
 * @var integer
 * @access protected
 */
	var $_transactionNesting = 0;

/**
 * Connects to the database using config['database'] as a filename.
 *
 * @param array $config Configuration array for connecting
 * @return mixed
 * @access public
 */
	function connect() {
		$this->last_error = null;
		$config = $this->config;
		try {
			$this->connection = new PDO($config['connect'].':'.$config['database'],null,null,array(PDO::ATTR_PERSISTENT => $config['persistent']));
			$this->connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
			$this->connected = is_object($this->connection);
		}
		catch(PDOException $e) {
			$this->last_error = array('Error connecting to database.',$e->getMessage());
		}
		return $this->connected;
	}

/**
 * Disconnects from database.
 *
 * @return boolean True if the database could be disconnected, else false
 * @access public
 */
	function disconnect() {
		$this->connection = NULL;
		$this->connected = false;
		return $this->connected;
	}

/**
 * Executes given SQL statement.
 *
 * @param string $sql SQL statement
 * @return resource Result resource identifier
 * @access protected
 */
	function _execute($sql) {
		if (strncmp($sql,"CREATE",6) === 0) {
			$statements = explode(";",$sql);
			if (count($statements) > 1) {
				foreach($statements as $st) {
					$this->_execute($st);
				}
				return false;
			}
		}
		for ($i = 0; $i < 2; $i++) {
			try {
				$this->last_error = NULL;
				$this->pdo_statement = $this->connection->query($sql);
				if (is_object($this->pdo_statement)) {
					$this->rows = $this->pdo_statement->fetchAll(PDO::FETCH_NUM);
					$this->row_count = count($this->rows);
					return $this->pdo_statement;
				}
	  		}
	  		catch(PDOException $e) {
	  			// Schema change; re-run query
				if ($e->errorInfo[1] === 17) {
					$this->last_error = $e->getMessage();
				}
				 continue;
	  		}
		}
		return false;
	}

/**
 * Returns an array of tables in the database. If there are no tables, an error is raised and the application exits.
 *
 * @return array Array of tablenames in the database
 * @access public
 */
	function listSources() {
		$db = $this->config['database'];
		$this->config['database'] = basename($this->config['database']);

		$cache = parent::listSources();
		if ($cache != null) {
			return $cache;
		}
		
		$result = $this->fetchAll("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;", false);

		if (!$result || empty($result)) {
			return array();
		} else {
			$tables = array();
			foreach ($result as $table) {
				$tables[] = $table[0]['name'];
			}
			parent::listSources($tables);

			$this->config['database'] = $db;
			return $tables;
		}
		$this->config['database'] = $db;
		return array();
	}

/**
 * Returns an array of the fields in given table name.
 *
 * @param string $tableName Name of database table to inspect
 * @return array Fields in table. Keys are name and type
 * @access public
 */
	function describe(&$model) {
		$cache = parent::describe($model);
		if ($cache != null) {
			return $cache;
		}
		$fields = array();
		$result = $this->fetchAll('PRAGMA table_info(' . $model->tablePrefix . $model->table . ')');

		foreach ($result as $column) {
			$fields[$column[0]['name']] = array(
				'type'		=> $this->column($column[0]['type']),
				'null'		=> !$column[0]['notnull'],
				'default'	=> $column[0]['dflt_value'],
				'length'	=> $this->length($column[0]['type'])
			);
			if($column[0]['pk'] == 1) {
				$fields[$column[0]['name']] = array(
					'type'		=> $fields[$column[0]['name']]['type'],
					'null'		=> false,
					'default'	=> $column[0]['dflt_value'],
					'key'		=> $this->index['PRI'],
					'length'	=> 11
				);
			}
		}

		$this->__cacheDescription($model->tablePrefix . $model->table, $fields);
		return $fields;
	}

/**
 * Returns a quoted and escaped string of $data for use in an SQL statement.
 *
 * @param string $data String to be prepared for use in an SQL statement
 * @return string Quoted and escaped
 * @access public
 */
	function value($data, $column = null, $safe = false) {
		$parent = parent::value($data, $column, $safe);

		if ($parent != null) {
			return $parent;
		}
		if ($data === null || (is_array($data) && empty($data))) {
			return 'NULL';
		}
		if ($data === '') {
			return  "''";
		}
		switch ($column) {
			case 'boolean':
				$data = $this->boolean((bool)$data);
			break;
			default:
				$data = $this->connection->quote($data);
				return $data;
			break;
		}
		return "'" . $data . "'";
	}

/**
 * Generates and executes an SQL UPDATE statement for given model, fields, and values.
 *
 * @param Model $model
 * @param array $fields
 * @param array $values
 * @param mixed $conditions
 * @return array
 * @access public
 */
	function update(&$model, $fields = array(), $values = null, $conditions = null) {
		if (empty($values) && !empty($fields)) {
			foreach ($fields as $field => $value) {
				if (strpos($field, $model->alias . '.') !== false) {
					unset($fields[$field]);
					$field = str_replace($model->alias . '.', "", $field);
					$field = str_replace($model->alias . '.', "", $field);
					$fields[$field] = $value;
				}
			}
		}
		return parent::update($model, $fields, $values, $conditions);
	}

/**
 * Begin a transaction
 *
 * @param unknown_type $model
 * @return boolean True on success, false on fail
 *    (i.e. if the database/model does not support transactions).
 * @access public
 */
	function begin(&$model) {
		if ($this->_transactionStarted || $this->connection->beginTransaction()) {
			$this->_transactionStarted = true;
			$this->_transactionNesting++;
			return true;
		}
		return false;
	}

/**
 * Commit a transaction
 *
 * @param unknown_type $model
 * @return boolean True on success, false on fail
 *    (i.e. if the database/model does not support transactions,
 *    or a transaction has not started).
 * @access public
 */
	function commit(&$model) {
		if ($this->_transactionStarted) {
			$this->_transactionNesting--;
			if ($this->_transactionNesting <= 0) {
				$this->_transactionStarted = false;
				$this->_transactionNesting = 0;
				return $this->connection->commit();
			}
			return true;
		}
		return false;
	}

/**
 * Rollback a transaction
 *
 * @param unknown_type $model
 * @return boolean True on success, false on fail
 *    (i.e. if the database/model does not support transactions,
 *    or a transaction has not started).
 * @access public
 */
	function rollback(&$model) {
		if ($this->_transactionStarted && $this->connection->rollBack()) {
			$this->_transactionStarted = false;
			$this->_transactionNesting = 0;
			return true;
		}
		return false;
	}

/**
 * Deletes all the records in a table and resets the count of the auto-incrementing
 * primary key, where applicable.
 *
 * @param mixed $table A string or model class representing the table to be truncated
 * @return boolean	SQL TRUNCATE TABLE statement, false if not applicable.
 * @access public
 */
	function truncate($table) {
		return $this->execute('DELETE From ' . $this->fullTableName($table));
	}

/**
 * Returns a formatted error message from previous database operation.
 *
 * @return string Error message
 * @access public
 */
	function lastError() {
		return $this->last_error;
	}

/**
 * Returns number of affected rows in previous database operation. If no previous operation exists, this returns false.
 *
 * @return integer Number of affected rows
 * @access public
 */
	function lastAffected() {
		if ($this->_result) {
			return $this->pdo_statement->rowCount();
		}
		return false;
	}

/**
 * Returns number of rows in previous resultset. If no previous resultset exists,
 * this returns false.
 *
 * @return mixed Number of rows in resultset, or false on error
 * @access public
 */
	function lastNumRows() {
		if ($this->pdo_statement) {
			// pdo_statement->rowCount() doesn't work for this case
			return $this->row_count;
		}
		return false;
	}

/**
 * Returns the ID generated from the previous INSERT operation.
 *
 * @return mixed Last insert ID
 * @access public
 */
	function lastInsertId() {
		return $this->connection->lastInsertId();
	}

/**
 * Converts database-layer column types to basic types
 *
 * @param string $real Real database-layer column type (i.e. "varchar(255)")
 * @return string Abstract column type (i.e. "string")
 * @access public
 */
	function column($real) {
		if (is_array($real)) {
			$col = $real['name'];
			if (isset($real['limit'])) {
				$col .= '('.$real['limit'].')';
			}
			return $col;
		}

		$col = strtolower(str_replace(')', '', $real));
		$limit = null;
		@list($col, $limit) = explode('(', $col);

		if (in_array($col, array('text', 'integer', 'float', 'boolean', 'timestamp', 'date', 'datetime', 'time'))) {
			return $col;
		}
		if (strpos($col, 'varchar') !== false) {
			return 'string';
		}
		if (in_array($col, array('blob', 'clob'))) {
			return 'binary';
		}
		if (strpos($col, 'numeric') !== false || strpos($col, 'decimal') !== false) {
			return 'float';
		}
		return 'text';
	}

/**
 * Generate ResultSet
 *
 * @param mixed $results
 * @access public
 */
	function resultSet(&$results) {
		$this->results =& $results;
		$this->map = array();
		$num_fields = $results->columnCount();
		$index = 0;
		$j = 0;

		//PDO::getColumnMeta is experimental and does not work with sqlite3,
		//	so try to figure it out based on the querystring
		$querystring = $results->queryString;
		if (stripos($querystring, 'SELECT') === 0) {
			$last = stripos($querystring, 'FROM');
			if ($last !== false) {
				$selectpart = substr($querystring, 7, $last - 8);
				$selects = explode(',', $selectpart);
			}
		} elseif (strpos($querystring, 'PRAGMA table_info') === 0) {
			$selects = array('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk');
		} elseif(strpos($querystring, 'PRAGMA index_list') === 0) {
			$selects = array('seq', 'name', 'unique');
		} elseif(strpos($querystring, 'PRAGMA index_info') === 0) {
			$selects = array('seqno', 'cid', 'name');
		}
		while ($j < $num_fields) {
			if (preg_match('/.*AS (.*).*/i', $selects[$j], $matches)) {
				 $columnName = trim($matches[1],'"');
			} else {
				$columnName = trim(str_replace('"', '', $selects[$j]));
			}

			if (strpos($selects[$j], 'DISTINCT') === 0) {
				$columnName = str_ireplace('DISTINCT', '', $columnName);
			}

			if (strpos($columnName, '.')) {
				$parts = explode('.', $columnName);
				$this->map[$index++] = array(trim($parts[0]), trim($parts[1]));
			} else {
				$this->map[$index++] = array(0, $columnName);
			}
			$j++;
		}
	}

/**
 * Fetches the next row from the current result set
 *
 * @return mixed
 * @access public
 */
	function fetchResult() {
		if (count($this->rows)) {
			$row = array_shift($this->rows);
			$resultRow = array();
			$i = 0;

			foreach ($row as $index => $field) {
				if (isset($this->map[$index]) and $this->map[$index] != "") {
					list($table, $column) = $this->map[$index];
					$resultRow[$table][$column] = $row[$index];
				} else {
					$resultRow[0][str_replace('"', '', $index)] = $row[$index];
				}
				$i++;
			}
			return $resultRow;
		}
		return false;
	}

/**
 * Returns a limit statement in the correct format for the particular database.
 *
 * @param integer $limit Limit of results returned
 * @param integer $offset Offset from which to start results
 * @return string SQL limit/offset statement
 * @access public
 */
	function limit ($limit, $offset = null) {
		if ($limit) {
			$rt = '';
			if (!strpos(strtolower($limit), 'limit') || strpos(strtolower($limit), 'limit') === 0) {
				$rt = ' LIMIT';
			}
			$rt .= ' ' . $limit;
			if ($offset) {
				$rt .= ' OFFSET ' . $offset;
			}
			return $rt;
		}
		return null;
	}

/**
 * Generate a database-native column schema string
 *
 * @param array $column An array structured like the following: array('name'=>'value', 'type'=>'value'[, options]),
 *    where options can be 'default', 'length', or 'key'.
 * @return string
 * @access public
 */
	function buildColumn($column) {
		$name = $type = null;
		$column = array_merge(array('null' => true), $column);
		extract($column);

		if (empty($name) || empty($type)) {
			trigger_error('Column name or type not defined in schema', E_USER_WARNING);
			return null;
		}

		if (!isset($this->columns[$type])) {
			trigger_error("Column type {$type} does not exist", E_USER_WARNING);
			return null;
		}

		$real = $this->columns[$type];
		$out = $this->name($name) . ' ' . $real['name'];
		if (isset($column['key']) && $column['key'] == 'primary' && $type == 'integer') {
			return $this->name($name) . ' ' . $this->columns['primary_key']['name'];
		}
		return parent::buildColumn($column);
	}

/**
 * Sets the database encoding
 *
 * @param string $enc Database encoding
 * @access public
 */
	function setEncoding($enc) {
		if (!in_array($enc, array("UTF-8", "UTF-16", "UTF-16le", "UTF-16be"))) {
			return false;
		}
		return $this->_execute("PRAGMA encoding = \"{$enc}\"") !== false;
	}

/**
 * Gets the database encoding
 *
 * @return string The database encoding
 * @access public
 */
	function getEncoding() {
		return $this->fetchRow('PRAGMA encoding');
	}

/**
 * Removes redundant primary key indexes, as they are handled in the column def of the key.
 *
 * @param array $indexes
 * @param string $table
 * @return string
 * @access public
 */
	function buildIndex($indexes, $table = null) {
		$join = array();

		foreach ($indexes as $name => $value) {

			if ($name == 'PRIMARY') {
				continue;
			}
			$out = 'CREATE ';

			if (!empty($value['unique'])) {
				$out .= 'UNIQUE ';
			}
			if (is_array($value['column'])) {
				$value['column'] = join(', ', array_map(array(&$this, 'name'), $value['column']));
			} else {
				$value['column'] = $this->name($value['column']);
			}
			$out .= "INDEX {$name} ON {$table}({$value['column']});";
			$join[] = $out;
		}
		return $join;
	}

/**
 * Overrides DboSource::index to handle SQLite indexe introspection
 * Returns an array of the indexes in given table name.
 *
 * @param string $model Name of model to inspect
 * @return array Fields in table. Keys are column and unique
 * @access public
 */
	function index(&$model) {
		$index = array();
		$table = $this->fullTableName($model);
		if ($table) {
			$indexes = $this->query('PRAGMA index_list(' . $table . ')');
			$tableInfo = $this->query('PRAGMA table_info(' . $table . ')');
			foreach ($indexes as $i => $info) {
				$key = array_pop($info);
				$keyInfo = $this->query('PRAGMA index_info("' . $key['name'] . '")');
				foreach ($keyInfo as $keyCol) {
					if (!isset($index[$key['name']])) {
						$col = array();
						if (preg_match('/autoindex/', $key['name'])) {
							$key['name'] = 'PRIMARY';
						}
						$index[$key['name']]['column'] = $keyCol[0]['name'];
						$index[$key['name']]['unique'] = intval($key['unique'] == 1);
					} else {
						if (!is_array($index[$key['name']]['column'])) {
							$col[] = $index[$key['name']]['column'];
						}
						$col[] = $keyCol[0]['name'];
						$index[$key['name']]['column'] = $col;
					}
				}
			}
		}
		return $index;
	}

/**
 * Overrides DboSource::renderStatement to handle schema generation with SQLite-style indexes
 *
 * @param string $type
 * @param array $data
 * @return string
 * @access public
 */
	function renderStatement($type, $data) {
		switch (strtolower($type)) {
			case 'schema':
				extract($data);

				foreach (array('columns', 'indexes') as $var) {
					if (is_array(${$var})) {
						${$var} = "\t" . join(",\n\t", array_filter(${$var}));
					}
				}
				return "CREATE TABLE {$table} (\n{$columns});\n{$indexes}";
			break;
			default:
				return parent::renderStatement($type, $data);
			break;
		}
	}

/**
 * PDO deals in objects, not resources, so overload accordingly.
 *
 * @return boolean
 * @access public
 */
	function hasResult() {
		return is_object($this->_result);
	}
}
