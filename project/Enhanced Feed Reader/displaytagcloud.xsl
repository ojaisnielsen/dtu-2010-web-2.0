<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml"
        encoding="UTF-8"
        doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

    <xsl:param name="title"/>

    <xsl:template match="/">
        <html>
            <body>
                <h1><xsl:value-of select="$title"/></h1>
                    <xsl:for-each select="//item">
                        <span>
                            <xsl:attribute name="style"><xsl:value-of select="concat('font-size: ', @grade, 'pt')"/></xsl:attribute>
                            <xsl:value-of select="."/>
                        </span>
                    </xsl:for-each>
            </body>
        </html>
    </xsl:template>


</xsl:stylesheet>
