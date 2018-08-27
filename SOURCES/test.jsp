<html>
   <head>
      <title>Test JSP Page</title>
      <style type="text/css">
         dt {
             float: left;
             width: 30%;
             text-align: right;
             padding: .25em;
             clear: left;
             font-weight: bold;
         }
         dd {
             float: left;
             width: 60%;
             padding: .25em 0;
         }
         dl:after {content:"";display:table;clear:both;} // will not work when there are mutli-dt per dd or multi-dd per dt
      </style>
   </head>
   <body>
      <h1>Test JSP Page</h1>
      <p>This is a page to verify that .jsp support has been enabled</p>
      <dl>
         <dt>Date</dt><dd><%= new java.util.Date() %></dd>
         <dt>Remote Address</dt><dd><%= request.getRemoteAddr() %></dd>
         <dt>Request Method</dt><dd><%= request.getMethod() %></dd>
         <dt>Servlet Path</dt><dd><%= request.getServletPath() %></dd>
         <dt>Tomcat Version</dt><dd><%= application.getServerInfo() %></dd>
         <dt>Servlet Specification Version</dt><dd><%= application.getMajorVersion() %>.<%= application.getMinorVersion() %></dd>
         <dt>JSP Version</dt><dd><%= JspFactory.getDefaultFactory().getEngineInfo().getSpecificationVersion() %></dd>
         <dt>JAVA_HOME</dt><dd><%= System.getenv("JAVA_HOME") %></dd>
         <dt>CATALINA_HOME</dt><dd><%= System.getenv("CATALINA_HOME") %></dd>
         <dt>CATALINA_BASE</dt><dd><%= System.getenv("CATALINA_BASE") %></dd>
         <dt>CATALINA_OPTS</dt><dd><%= System.getenv("CATALINA_OPTS") %></dd>
         <dt>USER</dt><dd><%= System.getenv("USER") %></dd>
         <dt>HOME</dt><dd><%= System.getenv("HOME") %></dd>
         <dt>Output from `id`</dt><dd><%@ page import="java.util.*,java.io.*"%>
      <%
        Process p = Runtime.getRuntime().exec("id");
        OutputStream outs = p.getOutputStream();
        InputStream ins = p.getInputStream();
        DataInputStream dis = new DataInputStream(ins);
        String disrl = dis.readLine();
        while ( disrl != null ) {
                out.println(disrl); 
                disrl = dis.readLine(); 
        }
       %></dd>
      </dl>
   </body>
</html>
