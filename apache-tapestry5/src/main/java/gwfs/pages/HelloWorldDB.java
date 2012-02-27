package gwfs.pages;

import gwfs.Hello;
import org.apache.tapestry5.annotations.Property;
import org.apache.tapestry5.ioc.annotations.Inject;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class HelloWorldDB {

    @Inject
    private DataSource dataSource;

    @Property
    private Hello hello;

    public List<Hello> getHellos() throws SQLException {

        List<Hello> result = new ArrayList<Hello>();

        Connection connection = null;

        try {
            connection = dataSource.getConnection();

            Statement stm = connection.createStatement();

            ResultSet rs = stm.executeQuery("select id, data from hello order by id asc");

            while (rs.next()) {
                Hello hello = new Hello(rs.getInt("id"), rs.getString("data"));
                result.add(hello);
            }
        } finally {
            connection.close();
        }

        return result;
    }


}
