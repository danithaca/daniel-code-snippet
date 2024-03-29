package quickfix;

import java.sql.*;

public class JDBCDemo {

        public static void main(String[] args) {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            // MYSQL JDBC
            Class.forName("com.mysql.jdbc.Driver");
            String conn_string = "jdbc:mysql://localhost:5000/drupal?user=drupal&password=tKayfDnu";
            conn = DriverManager.getConnection(conn_string);

            stmt = conn.createStatement();
            rs = stmt.executeQuery("select nid from node");
            while (rs.next()) {
                String name = rs.getString("nid");
                System.out.printf("%s\n", name);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } finally {
            // it is a good idea to release resources in a finally{} block in reverse-order of their creation
            //  if they are no-longer needed
            try {
                if (rs != null) rs.close();
                if (stmt != null) stmt.close();
                if (conn != null) conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}

