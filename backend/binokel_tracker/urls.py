"""
URL configuration for binokel_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import JsonResponse
from django.urls import path

from scoring.views import (
    punktestaende_view,
    runden_view,
    sieger_view,
    spiel_detail_view,
    spiele_view,
)


def healthcheck(request):
    """Minimaler Healthcheck-Endpunkt für den Deployment-Pipeline-Check."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # /admin/ ist in V1 bewusst NICHT geroutet (Sicherheits-Audit RD-6): kein
    # Superuser-Workflow nötig, und eine internet-exponierte Admin-Oberfläche ohne
    # Web-Rate-Limiting (fail2ban schützt nur sshd) wäre unnötige Angriffsfläche.
    # Reaktivieren: django.contrib.admin importieren + path("admin/", ...) hinzufügen,
    # dann zwingend per Nginx-IP-Allowlist absichern.
    path("health/", healthcheck, name="healthcheck"),
    # Slice 1: Spiel anlegen / laden
    path("api/spiele/", spiele_view, name="spiele"),
    path("api/spiele/<int:spiel_id>/", spiel_detail_view, name="spiel-detail"),
    # Slices 2–5: Runde auswerten
    path("api/spiele/<int:spiel_id>/runden/", runden_view, name="runden"),
    # Slice 6: Punktestände und Sieger
    path("api/spiele/<int:spiel_id>/punktestaende/", punktestaende_view, name="punktestaende"),
    path("api/spiele/<int:spiel_id>/sieger/", sieger_view, name="sieger"),
]
