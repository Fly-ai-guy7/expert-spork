{{- define "equalise.labels" -}}
app.kubernetes.io/name: {{ .Release.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}

{{- define "equalise.envFrom" -}}
- secretRef:
    name: {{ .Values.existingSecret }}
- configMapRef:
    name: {{ .Release.Name }}-config
{{- end }}
