{{/*
Expand the name of the chart.
*/}}
{{- define "heart-disease-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "heart-disease-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "heart-disease-api.labels" -}}
helm.sh/chart: {{ include "heart-disease-api.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "heart-disease-api.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "heart-disease-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "heart-disease-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
