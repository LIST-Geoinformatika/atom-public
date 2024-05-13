from django.urls import path

from inspire import views

urlpatterns = [
    path(
        "atom/",
        views.DownloadServiceEntryFeedView.as_view(),
        name="download-service-entry-feed",
    ),
    path(
        "atom/en/",
        views.DownloadServiceEntryFeedView.as_view(),
        name="download-service-entry-feed_EN",
        kwargs={"lng": "en"},
    ),
    path(
        "atom/search",
        views.OpenSearchQueryView.as_view(),
        name="opensearch-search",
    ),
    path(
        "atom/described-search",
        views.OpenSearchDesribedQueryView.as_view(),
        name="opensearch-described-search",
    ),
    path(
        "atom/service/<str:service_name>/",
        views.DatasetServiceFeedView.as_view(),
        name="dataset-feed",
    ),
    path(
        "atom/service/<str:service_name>/en/",
        views.DatasetServiceFeedView.as_view(),
        name="dataset-feed_EN",
        kwargs={"lng": "en"},
    ),
    path(
        "atom/opensearch-description",
        views.DownloadServiceOpenSearchView.as_view(),
        name="download-service-opensearch",
    ),
    path(
        "atom/opensearch-description/en/",
        views.DownloadServiceOpenSearchView.as_view(),
        name="download-service-opensearch_EN",
        kwargs={"lng": "en"},
    ),
]
