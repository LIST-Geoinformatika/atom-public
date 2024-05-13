from inspire import models

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize
from django.http import HttpResponse, FileResponse, HttpRequest
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import FieldError


class DownloadServiceEntryFeedView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        current_site = Site.objects.get_current()
        base_url = f"https://{current_site.domain}"

        # Retrieve data from the model
        download_service_feed = models.DownloadServiceEntryFeed.objects.first()
        dataset_entries = models.DatasetServiceFeed.objects.all()
        lng = kwargs.get("lng")
        # Build the XML string with all dataset entries
        xml_entries = ""
        for entry in dataset_entries:
            # CRSs available for each entry (dataset)
            crss = entry.available_crs.all()
            print(crss)

            xml_entries += f"""
                <entry>
                    <title>{entry.title if not lng else entry.title_EN}</title>
                    <inspire_dls:spatial_dataset_identifier_code>{entry.spatial_dataset_identifier_code}</inspire_dls:spatial_dataset_identifier_code>
                    <inspire_dls:spatial_dataset_identifier_namespace>{entry.spatial_dataset_identifier_namespace}</inspire_dls:spatial_dataset_identifier_namespace>
                    <link href="{entry.metadata_record}" rel="describedby" type="application/xml"/>
                    <link rel="alternate" href="{base_url}{reverse('dataset-feed' if lng else 'dataset-feed_EN', kwargs={"service_name": entry.service_name})}" type="application/atom+xml" hreflang="{"hr" if not lng else "en"}" 
                    title="{"Dokument koji sadrži pripremljeni skup podataka (u jednom formatu za preuzimanje ili više njih)" if not lng else "Document containing pre-defined dataset (in single or multiple formats)" }"/>
                    <id>{base_url}{reverse('dataset-feed' if not lng else 'dataset-feed_EN', kwargs={"service_name": entry.service_name})}</id>
                    <rights>{entry.rights if not lng else entry.rights_EN}</rights>
                    <updated>{entry.updated_on.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
                    <summary>{entry.summary if not lng else entry.summary_EN}</summary>
                    <georss:polygon>47.202 5.755 55.183 5.755 55.183 15.253 55.183 5.755 47.202 5.755</georss:polygon>
                    {"".join([f'<category term="{crs.opengis_label}" label="{crs.label}"/>' for crs in crss])}
                </entry>
            """

        # Build the complete XML string of entry point ATOM feed
        xml_content = f"""
            <feed xmlns="http://www.w3.org/2005/Atom"
            xmlns:georss="http://www.georss.org/georss"
            xmlns:inspire_dls="http://inspire.ec.europa.eu/schemas/inspire_dls/1.0"
            xml:lang="hr">
            <title>{download_service_feed.title if not lng else download_service_feed.title_EN}</title>
            <subtitle>{download_service_feed.subtitle if not lng else download_service_feed.subtitle_EN}</subtitle>
            <link href="{download_service_feed.link_to_download_service_iso19139}"
            rel="describedby" type="application/xml"/>
            <link href="{base_url}{reverse('download-service-entry-feed' if not lng else 'download-service-entry-feed_EN')}" rel="self"
            type="application/atom+xml"
            hreflang="{"hr" if not lng else "en"}" title="{"Ovaj dokument" if not lng else "This document"}"/>
            <link rel="search" href="{base_url}{reverse('download-service-opensearch' if not lng else 'download-service-opensearch_EN')}"
            type="application/opensearchdescription+xml" title="{"Open Search opis usluge preuzimanja" if not lng else "Open Search download service description"}"/>
            <link href="{base_url}{reverse('download-service-entry-feed' if lng else 'download-service-entry-feed_EN')}" rel="alternate"
            type="application/atom+xml" hreflang="{"en" if not lng else "hr"}"
            title="{"Download service info in English" if not lng else "Informacije usluge preuzimanja na hrvatskom jeziku" }"/>
            <id>{base_url}{reverse('download-service-entry-feed' if not lng else 'download-service-entry-feed_EN')}</id>
            <rights>{download_service_feed.rights if not lng else download_service_feed.rights_EN}</rights>
            <updated>{download_service_feed.updated_on.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
            <author>
            <name>{download_service_feed.author_name}</name>
            <email>{download_service_feed.author_email}</email>
            </author>
            {xml_entries}
        </feed>
        """

        # Remove leading whitespaces or characters
        xml_content = xml_content.strip()
        return HttpResponse(xml_content, content_type="application/xml")


class DatasetServiceFeedView(APIView):
    permission_classes = []

    def get(self, request, service_name, *args, **kwargs):
        current_site = Site.objects.get_current()
        base_url = f"https://{current_site.domain}"

        lng = kwargs.get("lng")

        # Retrieve data from the model
        dataset_service_feed = models.DatasetServiceFeed.objects.filter(
            service_name=service_name
        ).first()

        # Initialize an empty string to accumulate XML entries
        xml_entries = ""

        # Get all related ServiceFeeds
        service_feeds = dataset_service_feed.servicefeed_set.all()

        # Iterate over ServiceFeeds and all CRS that exist for that service
        for service_feed in service_feeds:
            harmonized_services = service_feed.harmonizeddatasetfile_set.all()

            for service_crs in harmonized_services:
                # Build XML block for each CRS
                crs = service_crs.crs

                xml_entries += f"""
                    <entry>
                        <title>{service_feed.title if not lng else service_feed.title_EN} {"u GML formatu u" if not lng else "in GML format in"} {crs.label} {"projekciji." if not lng else "projection."}</title>
                        <link rel="alternate"
                            href="{base_url}{service_crs.file.url}" type="application/xml" hreflang="hr" length="89274"
                            title="{service_feed.title if not lng else service_feed.title_EN} {"u GML formatu u" if not lng else "in GML format in"} {crs.label} {"projekciji." if not lng else "projection."}"/>
                        <id>{base_url}{service_crs.file.url}</id>
                        <updated>{service_crs.uploaded_on.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
                        <category term="{crs.opengis_label}"
                            label="{crs.label}"/>
                    </entry>
                """

        # Build the complete XML string
        xml_content = f"""
            <feed xmlns="http://www.w3.org/2005/Atom"
                xmlns:georss="http://www.georss.org/georss" xml:lang="en">
                <title>{dataset_service_feed.title if not lng else dataset_service_feed.title_EN}</title>
                <subtitle>{dataset_service_feed.subtitle if not lng else dataset_service_feed.subtitle_EN}</subtitle>
                <link href="http://inspireregistry.jrc.ec.europa.eu/registers/FCD/items/105" rel="describedby"
                    type="text/html"/>
                <link href="http://inspireregistry.jrc.ec.europa.eu/registers/FCD/items/412" rel="describedby"
                    type="text/html"/>                  
                <link href="{base_url}{reverse('dataset-feed' if not lng else 'dataset-feed_EN', kwargs={"service_name": dataset_service_feed.service_name})}" rel="self"
                    type="application/atom+xml"
                    hreflang="{"hr" if not lng else "en"}" title="{"Ovaj dokument" if not lng else "This document"}"/> 
                <link href="{base_url}{reverse('dataset-feed' if lng else 'dataset-feed_EN', kwargs={"service_name": dataset_service_feed.service_name})}" rel="alternate"
                    type="application/atom+xml" hreflang="{"en" if not lng else "hr"}"
                    title="{"This document in English" if not lng else "Ovaj dokument na hrvatskom jeziku" }"/>
                <link href="{reverse('download-service-entry-feed' if not lng else 'download-service-entry-feed_EN')}" rel="up"
                    type="application/atom+xml" hreflang="{"hr" if not lng else "en"}" title="{"Dokument izvorišnog servisa" if not lng else "The parent service feed document"}"/>
                <id>{base_url}{reverse('dataset-feed' if not lng else 'dataset-feed_EN', kwargs={"service_name": dataset_service_feed.service_name})}</id>
                <rights>{dataset_service_feed.rights if not lng else dataset_service_feed.rights_EN}</rights>
                <updated>{dataset_service_feed.updated_on.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
                <author>
                    <name>{dataset_service_feed.author_name}</name>
                    <email>{dataset_service_feed.author_email}</email>
                </author>
                {xml_entries}
            </feed>
        """

        # Remove leading whitespaces or characters
        xml_content = xml_content.strip()
        return HttpResponse(xml_content, content_type="application/xml")


class DownloadServiceOpenSearchView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):

        lng = kwargs.get("lng")

        # Retrieve data from the model
        download_service_feed = models.DownloadServiceEntryFeed.objects.first()
        dataset_entries = models.DatasetServiceFeed.objects.all()
        # Build the XML string with dataset entries
        xml_entries = ""
        current_site = Site.objects.get_current()
        base_url = f"https://{current_site.domain}"
        # Create example for each dataset
        for dataset in dataset_entries:

            # For each service_feed in dataset
            for service_feed in dataset.servicefeed_set.all():
                harmonized_services = service_feed.harmonizeddatasetfile_set.all()
                # For each crs available on each service_feed
                for service_crs in harmonized_services:
                    # Build XML block for each CRS
                    crs = service_crs.crs
                    xml_entries += f"""
                        <Query role="example" inspire_dls:spatial_dataset_identifier_namespace="{dataset.spatial_dataset_identifier_namespace}" inspire_dls:spatial_dataset_identifier_code="{dataset.spatial_dataset_identifier_code}" inspire_dls:crs="EPSG:{crs.epsg_code}" language="hr" title="{service_feed.title}" count="1"/>
                    """

        # Build the complete XML string
        xml_content = f"""
                <OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/"
        xmlns:inspire_dls="http://inspire.ec.europa.eu/schemas/inspire_dls/1.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://a9.com/-/spec/opensearch/1.1/ OpenSearch.xsd">
        <ShortName>{"Geoportal Ministarstva poljoprivrede – Pretraga INSPIRE ATOM usluge preuzimanja" if not lng else "Ministry of Agriculture Geoportal - INSPIRE ATOM service search"}</ShortName>
        <Description>{"Pretraga i opis skupova podataka dijeljenih INSPIRE ATOM uslugom preuzimanja Geoportala Ministarstva poljoprivrede" if not lng else "Search and description of INSPIRE datasets shared using Geoportal ATOM service from Ministry of Agriculture" }</Description>
        <!--URL of this document-->
        <Url type="application/opensearchdescription+xml" rel="self"
        template="{base_url}{reverse('download-service-opensearch' if not lng else 'download-service-opensearch_EN')}"/>
        <!--Generic URL template for browser integration-->
        <Url type="text/html" rel="results"
        template="{base_url}{reverse('opensearch-search')}?q={{searchTerms}}"/>
        <!--Describe Spatial Data Set Operation request URL template to be used
        in order to retrieve the description of Spatial Object Types in a Spatial
        Dataset-->
        <Url type="application/atom+xml" rel="describedby"
        template="{base_url}{reverse('opensearch-search')}?spatial_dataset_identifier_code={{inspire_dls:spatial_dataset_identifier_code?}}&amp;spatial_dataset_identifier_name
        space={{inspire_dls:spatial_dataset_identifier_namespace?}}&amp;crs={{inspire_dls:crs?}}&amp;language={{language?}}&amp;q={{searchTerms?}}"/>
        <!--Get Spatial Data Set Operation request URL template to be used in
        order to retrieve a Spatial Dataset-->
        <Url type="application/zip" rel="results"
        template="{base_url}{reverse('opensearch-search')}?spatial_dataset_identifier_code={{inspire_dls:spatial_dataset_identifier_code?}}&amp;spatial_dataset_identifier_namespace={{inspire_dls:spatial_dataset_identifier_namespace?}}&amp;crs={{inspire_dls:crs?}}&amp;language={{language?}}&amp;q={{searchTerms?}}"/>
        <Contact>geoportal.info@mps.hr</Contact>
        <Tags>{"Ministarstvo poljoprivrede servis za preuzimanje - ATOM INSPIRE" if not lng else "Ministry of Agriculture - download service - ATOM INSPIRE"}</Tags>
        <LongName>{"Opensearch pretraga servisa za preuzimanje - ATOM INSPIRE, Ministarstva poljoprivrede" if not lng else "Opensearch download service search - ATOM INSPIRE, Ministry of Agriculture"}</LongName>
        <Image height="16" width="16"
        type="image/png">http://xyz.org/waternetworkSearch.png</Image>
        <!--List of available Spatial Dataset Identifiers -->
        {xml_entries}
        <Developer>{"Ministarstvo Poljoprivrede" if not lng else "Ministry of Agriculture"}</Developer>
        <!--Languages supported by the service. The first language is the
        default language-->
        <Language>hr</Language>
        <Language>en</Language>
        </OpenSearchDescription>
        """

        # Remove leading whitespaces or characters
        xml_content = xml_content.strip()
        return HttpResponse(xml_content, content_type="application/xml")


class OpenSearchQueryView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):

        queryset = models.ServiceFeed.objects.all()

        query_params = request.query_params

        if len(list(query_params)) < 1:
            return Response(
                "Resource was requested without parameters",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            for key, value in query_params.items():
                if key == "spatial_dataset_identifier_code":
                    queryset = queryset.filter(
                        dataset__spatial_dataset_identifier_code=value
                    )
                elif key == "spatial_dataset_identifier_namespace":
                    queryset = queryset.filter(
                        dataset__spatial_dataset_identifier_namespace=value
                    )
                elif key == "crs":
                    # Filter ServiceFeed instances based on related HarmonizedDatasetFile's CRS
                    queryset = queryset.filter(
                        harmonizeddatasetfile__crs__epsg_code=value.replace("EPSG:", "")
                    ).distinct()
                elif key == "language":
                    # TODO implement language - Curently only default language is returned which is okay since there is only one possible language per ServiceFeed
                    queryset = queryset
                elif key == "count":  # Count can be ignored
                    queryset = queryset
                else:
                    queryset = queryset.filter(**{key: value})
        except FieldError as e:
            return Response(
                "Unkown search parameters used!", status=status.HTTP_400_BAD_REQUEST
            )

        results = list(queryset)

        if len(results) > 0:
            file_location = results[0].harmonizeddatasetfile_set.first()
            return FileResponse(file_location.file.file, content_type="application/zip")
        else:
            return Response(
                "No record matches query params!", status=status.HTTP_404_NOT_FOUND
            )


class OpenSearchDesribedQueryView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):

        # Filtering is on datasets
        queryset = models.DatasetServiceFeed.objects.all()

        query_params = request.query_params

        if len(list(query_params)) < 1:
            return Response(
                "Resource was requested without parameters",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            for key, value in query_params.items():
                if key == "crs":
                    queryset = queryset  # Ignore CRS on this endpoint
                elif key == "language":  # TODO implement language
                    queryset = queryset
                elif key == "count":  # Count can be ignored
                    queryset = queryset
                else:
                    queryset = queryset.filter(**{key: value})
        except FieldError as e:
            return Response(
                "Unkown search parameters used!", status=status.HTTP_400_BAD_REQUEST
            )

        results = list(queryset)

        if len(results) == 1:
            # If dataset was found return same result as for classic ATOM feed of dataset

            new_get_params = request.GET.copy()
            new_get_params["service_name"] = results[0].service_name

            # Convert DRF's Request object to Django's HttpRequest
            django_request = HttpRequest()
            django_request.method = request.method

            new_response = DatasetServiceFeedView.as_view()(
                django_request, service_name=results[0].service_name
            )

            if new_response:
                return new_response
            else:
                return Response(
                    "Something went wrong!",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif len(results) > 1:
            return Response(
                "Multiple datasets found, please contact administrator!",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        else:
            return Response(
                "No record matches query params!", status=status.HTTP_404_NOT_FOUND
            )
