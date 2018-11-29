{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 26 -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 24 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 26 -}}
{{- end -}}

{{/*
Get the default service name
*/}}
{{- define "service.name" -}}
{{- if .Values.serviceNameOverride  }}
{{- printf "%s-service" .Values.serviceNameOverride -}}
{{ else }}
{{- printf "%s-service" .Chart.Name -}}
{{- end -}}
{{- end -}}