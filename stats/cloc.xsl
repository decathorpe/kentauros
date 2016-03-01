<?xml version="1.0" encoding="US-ASCII"?>
<!-- XLS file by Paul Schwann, January 2009.
     Fixes for by-file and by-file-by-lang by d_uragan, November 2010.
     -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>CLOC Results</title>
      </head>
      <style type="text/css">
        table {
          table-layout: auto;
          border-collapse: collapse;
          empty-cells: show;
        }
        td, th {
          padding: 4px;
        }
        th {
          background-color: #CCCCCC;
        }
        td {
          text-align: center;
        }
        table, td, tr, th {
          border: thin solid #999999;
        }
      </style>
      <body>
        <h3><xsl:value-of select="results/header"/></h3>
       <table>
          <thead>
            <tr>
              <th>Language</th>
              <th>Files</th>
              <th>Blank</th>
              <th>Comment</th>
              <th>Code</th>
           </tr>
          </thead>
          <tbody>
          <xsl:for-each select="results/languages/language">
            <tr>
              <th><xsl:value-of select="@name"/></th>
              <td><xsl:value-of select="@files_count"/></td>
              <td><xsl:value-of select="@blank"/></td>
              <td><xsl:value-of select="@comment"/></td>
              <td><xsl:value-of select="@code"/></td>
          </tr>
          </xsl:for-each>
            <tr>
              <th>Total</th>
              <th><xsl:value-of select="results/languages/total/@sum_files"/></th>
              <th><xsl:value-of select="results/languages/total/@blank"/></th>
              <th><xsl:value-of select="results/languages/total/@comment"/></th>
              <th><xsl:value-of select="results/languages/total/@code"/></th>
           </tr>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>

