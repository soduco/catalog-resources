<?xml version="1.0"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:oai="http://www.openarchives.org/OAI/2.0/"
    xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xpath-default-namespace="http://www.openarchives.org/OAI/2.0/">
<xsl:output method="text" indent="yes"/>
<xsl:strip-space elements="*"/>
<xsl:variable name='newline'><xsl:text>
</xsl:text></xsl:variable>

<xsl:template match="/oai:OAI-PMH">
<!-- <xsl:text>oaipmh
</xsl:text> -->
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="oai:responseDate"/>

<xsl:template match="oai:request">
<xsl:text>---
type: "Instantiation"
identifier: </xsl:text>
<!-- <xsl:value-of select="concat(@identifier,$newline)"/> -->
<xsl:value-of select="concat(.,'?verb=',@verb,'&amp;metadataPrefix=',@metadataPrefix,'&amp;identifier=',@identifier,$newline)"/>
</xsl:template>

<xsl:template match="oai:GetRecord/oai:record">
<xsl:text>title: </xsl:text>
<!-- <xsl:for-each select="distinct-values(//dc:title)">
    <xsl:value-of select="."/>
    <xsl:if test="position()!=last()"><xsl:text>; </xsl:text></xsl:if>
</xsl:for-each> -->
<xsl:value-of select="//dc:title[position()=1]"/>
<xsl:text>
</xsl:text>
<xsl:text>pub_title: </xsl:text><xsl:value-of select="//dc:title[position()=2]"/>
<xsl:text>
</xsl:text>
<xsl:text>short_title: </xsl:text><xsl:value-of select="//dc:title[position()=3]"/>
<xsl:text>
</xsl:text>
<xsl:text>overview: </xsl:text><xsl:value-of select="//dc:identifier[position()=2]"/>
<xsl:text>
presentationForm: "mapDigital"
associatedResource:
    -
        value: "5983d5b5-46f3-4189-925c-c5df8fa36a0b"
        typeOfAssociation: "largerWorkCitation"
distributionInfo:
    -
        distributionFormat: "JPEG2000"
        transferOptions: 
            -
                linkage: "</xsl:text>
<xsl:value-of select="substring-after(substring-before(//dc:format,' target'),'href=')"/>
<xsl:text>"
                protocol: "WWW:LINK"
                name: "Original scan from the D. Rumsey map collection"
                typeOfTransferOption: "OnlineResource"
</xsl:text>
<xsl:apply-templates/>
<xsl:text>extent:
    temporalExtent:
        beginPosition: "</xsl:text>
<xsl:for-each select="concat(min(//dc:date/text()),'-01-01')">
    <xsl:value-of select="."/>
</xsl:for-each>
<xsl:text>"
        endPosition: "</xsl:text>
<xsl:for-each select="concat(max(//dc:date/text()),'-01-01')">
    <xsl:value-of select="."/>
</xsl:for-each>
<xsl:text>"
</xsl:text>
<xsl:text>stakeholders:</xsl:text>
<xsl:for-each select="distinct-values(//dc:creator)">
<xsl:text>
    -
        role: "originator"
        name: </xsl:text>
        <xsl:value-of select="."/>
    <!-- <xsl:if test="position()!=last()"><xsl:text>; </xsl:text></xsl:if> -->
</xsl:for-each>
<xsl:text>
    -
        role: "publisher"
        name: "David Rumsey Map Collection"
...
</xsl:text>
<!-- <xsl:for-each select="distinct-values(//dc:identifier)">
    <xsl:value-of select="."/>
</xsl:for-each> -->
<!-- <xsl:text>
</xsl:text> -->
</xsl:template>

<xsl:template match="oai:header"/>

<xsl:template match="dc:identifier"/>
<!-- <xsl:template match="dc:identifier">
    <xsl:text>dc_identifier = </xsl:text><xsl:value-of select="concat(.,$newline)"/>
</xsl:template> -->

<xsl:template match="dc:coverage"/>

<!-- <xsl:template match="dc:date">
    <xsl:text>date = </xsl:text><xsl:value-of select="concat(.,$newline)"/>
</xsl:template> -->

<xsl:template match="dc:date"/>
<xsl:template match="dc:creator"/>
<!-- <xsl:template match="dc:creator">
    <xsl:text>creator = </xsl:text><xsl:value-of select="concat(.,$newline)"/>
</xsl:template> -->

<xsl:template match="dc:format"/>

<xsl:template match="dc:description"/>

<xsl:template match="dc:title"/>

<xsl:template match="dc:type"/>

<xsl:template match="dc:relation"/>

<xsl:template match="dc:publisher"/>

</xsl:stylesheet>