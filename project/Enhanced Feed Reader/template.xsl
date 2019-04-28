<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:efr="EnhancedFeedReader"
    xmlns:str="http://exslt.org/strings"
    xmlns:set="http://exslt.org/sets">

    <xsl:output method="xml"
        encoding="UTF-8"
        doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>


    <xsl:param name="start"/>
    <xsl:param name="end"/>

    <xsl:template match="/">

        <html>
            <head>
                <title>Enhanced Feed Reader</title>
                <link rel="stylesheet" type="text/css">
                    <xsl:attribute name="href">
                        <xsl:value-of select="efr:getFullUrl('style.css')"/>
                    </xsl:attribute>
                </link>
                <script type="text/javascript">
                    <xsl:attribute name="src">
                        <xsl:value-of select="efr:getFullUrl('dynamic.js')"/>
                    </xsl:attribute>
                    <xsl:comment/>
                </script>

            </head>
            <body>
                <form id="entities" onsubmit="return false">
                    <ul>

                        <xsl:for-each select="set:distinct(/efrDb/entry/head/entity/@type)">
                            <li>
                                <xsl:value-of select="."/>
                        
                                <input type="text">
                                    <xsl:attribute name="name">
                                        <xsl:value-of select="."/>
                                    </xsl:attribute>
                                    <xsl:attribute name="onkeyup">
                                        <xsl:value-of select="concat('selectEntity(&quot;', ., '/&quot; + document.getElementById(&quot;entities&quot;).elements[&quot;', ., '&quot;].value)', '; updateSubmitter()')"/>
                                    </xsl:attribute>
                                </input>
                            </li>
                        </xsl:for-each>
                    </ul>
                    <a id="submit" href="efr:search">Search references</a>
                </form>
                <ul id="entries">

                    <xsl:for-each select="/efrDb/entry[count(preceding-sibling::entry) &gt;= $start and count(preceding-sibling::entry) &lt; $end]">
                        <li class="ENTRY">
                            <xsl:attribute name="id">
                                <xsl:value-of select="count(preceding-sibling::entry)"/>
                            </xsl:attribute>
                            <xsl:if test="number(count(preceding-sibling::entry)) mod 2 = 0">
                                <xsl:attribute name="class">
                                    <xsl:text>ENTRY EVEN</xsl:text>
                                </xsl:attribute>
                            </xsl:if>
                            <div class="MAIN" >
                                <h1>
                                    <a>
                                        <xsl:attribute name="href">
                                            <xsl:value-of select="@link"/>
                                        </xsl:attribute>
                                        <xsl:value-of select="@title"/>
                                    </a>
                                </h1>
                                <h2>
                                    <xsl:value-of select="@date"/>
                                </h2>
                                <xsl:apply-templates select="body/*"/>
                            </div>
                            <div class="EXTRA">
                                <ul>
                                    <xsl:for-each select="head/entity">
                                        <li>
                                            <xsl:if test="position() = 1">
                                                <xsl:attribute name="style">display: inline</xsl:attribute>
                                            </xsl:if>
                                            <xsl:attribute name="id">
                                                <xsl:value-of select="concat(ancestor::entry/@id, '/', @type, '/', .)"/>
                                            </xsl:attribute>

                                            <xsl:choose>

                                                <xsl:when test="@type = 'LOCATION'">
                                                    <object type="text/html" class="MAP">
                                                        <xsl:attribute name="data">
                                                            <xsl:value-of select="efr:getMapUrl(string(.))"/>
                                                        </xsl:attribute>    
                                                    </object>

                                                </xsl:when>
                                           
                                                <xsl:when test="@type = 'PERSON'">
                                                    <xsl:copy-of select="efr:getTweets(string(.))"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:copy-of select="efr:getGoogleSearch(string(.))"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                            </div>
                        </li>
                    </xsl:for-each>
                </ul>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:choose>
                <xsl:when test="contains(@class, 'ENTITY') and not(@title = '')">
                    <xsl:attribute name="onMouseOver">
                        <xsl:value-of select="concat('displayInfo(&quot;', ancestor::entry/@id, '/',  str:tokenize(@class)[2], '/', @title, '&quot;)')"/>
                    </xsl:attribute>
                    <xsl:attribute name="onClick">
                        <xsl:value-of select="concat('selectEntity(&quot;', str:tokenize(@class)[2], '/', @title, '&quot;)', '; updateSubmitter()')"/>
                    </xsl:attribute>
                    <xsl:apply-templates select="@*|node()"/>
            </xsl:when>
            <xsl:when test="contains(@class, 'ENTITY') and @title = ''">
                 <xsl:apply-templates select="node()"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates select="@*|node()"/>
            </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
