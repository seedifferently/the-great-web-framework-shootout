dataSource {
    pooled = true
	dbCreate = "validate"
	url = "jdbc:sqlite:hello.db"
    driverClassName = "org.sqlite.JDBC"
	// we use the MySQL dialect as a generic substitute for SQLite
	dialect = "org.hibernate.dialect.MySQLDialect"
}
hibernate {
    cache.use_second_level_cache = true
    cache.use_query_cache = true
    cache.region.factory_class = 'net.sf.ehcache.hibernate.EhCacheRegionFactory'
}