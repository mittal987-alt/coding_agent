{{/*
============================================================
Expand Chart Name
============================================================
*/}}

{{- define "ai-platform.name" -}}

{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" -}}

{{- end }}

{{/*
============================================================
Full Resource Name
============================================================
*/}}

{{- define "ai-platform.fullname" -}}

{{- if .Values.global.fullnameOverride }}

{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}

{{- else }}

{{- printf "%s-%s" .Release.Name (include "ai-platform.name" .) | trunc 63 | trimSuffix "-" }}

{{- end }}

{{- end }}

{{/*
============================================================
Chart Label
============================================================
*/}}

{{- define "ai-platform.chart" -}}

{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}

{{- end }}

{{/*
============================================================
Selector Labels
============================================================
*/}}

{{- define "ai-platform.selectorLabels" -}}

app.kubernetes.io/name: {{ include "ai-platform.name" . }}

app.kubernetes.io/instance: {{ .Release.Name }}

{{- end }}

{{/*
============================================================
Common Labels
============================================================
*/}}

{{- define "ai-platform.labels" -}}

helm.sh/chart: {{ include "ai-platform.chart" . }}

{{ include "ai-platform.selectorLabels" . }}

app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}

app.kubernetes.io/managed-by: {{ .Release.Service }}

{{- with .Values.commonLabels }}

{{ toYaml . }}

{{- end }}

{{- end }}

{{/*
============================================================
Common Annotations
============================================================
*/}}

{{- define "ai-platform.annotations" -}}

{{- with .Values.commonAnnotations }}

{{ toYaml . }}

{{- end }}

{{- end }}

{{/*
============================================================
Service Account
============================================================
*/}}

{{- define "ai-platform.serviceAccountName" -}}

{{- if .Values.serviceAccount.create }}

{{- default (include "ai-platform.fullname" .) .Values.serviceAccount.name }}

{{- else }}

default

{{- end }}

{{- end }}

{{/*
============================================================
Backend Image
============================================================
*/}}

{{- define "ai-platform.backend.image" -}}

{{ printf "%s:%s"
    .Values.images.backend.repository
    .Values.images.backend.tag }}

{{- end }}

{{/*
============================================================
Frontend Image
============================================================
*/}}

{{- define "ai-platform.frontend.image" -}}

{{ printf "%s:%s"
    .Values.images.frontend.repository
    .Values.images.frontend.tag }}

{{- end }}

{{/*
============================================================
Worker Image
============================================================
*/}}

{{- define "ai-platform.worker.image" -}}

{{ printf "%s:%s"
    .Values.images.worker.repository
    .Values.images.worker.tag }}

{{- end }}

{{/*
============================================================
Code Executor Image
============================================================
*/}}

{{- define "ai-platform.executor.image" -}}

{{ printf "%s:%s"
    .Values.images.codeExecutor.repository
    .Values.images.codeExecutor.tag }}

{{- end }}

{{/*
============================================================
Secret Name
============================================================
*/}}

{{- define "ai-platform.secretName" -}}

{{ default
    (printf "%s-secret" (include "ai-platform.fullname" .))
    .Values.secrets.existingSecret }}

{{- end }}

{{/*
============================================================
ConfigMap Name
============================================================
*/}}

{{- define "ai-platform.configMapName" -}}

{{ printf "%s-config"
    (include "ai-platform.fullname" .) }}

{{- end }}

{{/*
============================================================
Backend Service
============================================================
*/}}

{{- define "ai-platform.backend.service" -}}

{{ printf "%s-backend"
    (include "ai-platform.fullname" .) }}

{{- end }}

{{/*
============================================================
Frontend Service
============================================================
*/}}

{{- define "ai-platform.frontend.service" -}}

{{ printf "%s-frontend"
    (include "ai-platform.fullname" .) }}

{{- end }}

{{/*
============================================================
Ingress Name
============================================================
*/}}

{{- define "ai-platform.ingressName" -}}

{{ printf "%s-ingress"
    (include "ai-platform.fullname" .) }}

{{- end }}

{{/*
============================================================
Namespace
============================================================
*/}}

{{- define "ai-platform.namespace" -}}

{{ default .Release.Namespace "ai-platform" }}

{{- end }}

{{/*
============================================================
Environment Variables
============================================================
*/}}

{{- define "ai-platform.env" -}}

{{- range $key, $value := .Values.env }}

- name: {{ $key }}

  value: {{ $value | quote }}

{{- end }}

{{- end }}

{{/*
============================================================
Pod Security Context
============================================================
*/}}

{{- define "ai-platform.podSecurityContext" -}}

{{ toYaml .Values.security.podSecurityContext }}

{{- end }}

{{/*
============================================================
Container Security Context
============================================================
*/}}

{{- define "ai-platform.containerSecurityContext" -}}

{{ toYaml .Values.security.containerSecurityContext }}

{{- end }}

{{/*
============================================================
Node Selector
============================================================
*/}}

{{- define "ai-platform.nodeSelector" -}}

{{ toYaml .Values.nodeSelector }}

{{- end }}

{{/*
============================================================
Affinity
============================================================
*/}}

{{- define "ai-platform.affinity" -}}

{{ toYaml .Values.affinity }}

{{- end }}

{{/*
============================================================
Tolerations
============================================================
*/}}

{{- define "ai-platform.tolerations" -}}

{{ toYaml .Values.tolerations }}

{{- end }}

{{/*
============================================================
Topology Spread Constraints
============================================================
*/}}

{{- define "ai-platform.topologySpreadConstraints" -}}

{{ toYaml .Values.topologySpreadConstraints }}

{{- end }}