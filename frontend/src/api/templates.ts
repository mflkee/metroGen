import { apiRequest } from "@/api/client";

export type TemplateOut = {
  id: string;
  title: string;
  instrument_kind: string;
  parent_code: string | null;
  children: string[];
  renderer: string;
  is_active: boolean;
  is_editable: boolean;
};

export type TemplateCatalog = {
  templates: TemplateOut[];
  instrument_kinds: string[];
  match_fields: string[];
};

export type TemplateRule = {
  id: number;
  instrument_kind: string;
  match_field: string;
  match_value: string;
  template_id: string;
  priority: number;
  is_active: boolean;
};

export type TemplateRulePayload = {
  instrument_kind: string;
  match_field: string;
  match_value: string;
  template_id: string;
  priority: number;
  is_active: boolean;
};

export type TemplateRuleBrief = {
  id: number;
  instrument_kind: string;
  match_field: string;
  match_value: string;
  priority: number;
  is_active: boolean;
};

export type TemplateFormDetail = {
  form: TemplateOut;
  rules: TemplateRuleBrief[];
};

export type TemplatePreviewStep = {
  stage: string;
  matched: boolean;
  rule_id: number | null;
  match_field: string | null;
  match_value: string | null;
  methodology_code: string | null;
  template_id: string | null;
};

export type TemplatePreview = {
  template_id: string;
  template_title: string | null;
  source: string;
  rule_id: number | null;
  steps: TemplatePreviewStep[];
};

export type TemplatePreviewPayload = {
  instrument_kind?: string | null;
  method_code?: string | null;
  mitype_number?: string | null;
  mitype_title?: string | null;
  modification?: string | null;
  override?: string | null;
};

export async function fetchTemplateCatalog(token: string): Promise<TemplateCatalog> {
  return apiRequest<TemplateCatalog>("/templates", { method: "GET", token });
}

export async function fetchTemplateForm(token: string, code: string): Promise<TemplateFormDetail> {
  return apiRequest<TemplateFormDetail>(`/templates/${encodeURIComponent(code)}`, {
    method: "GET",
    token,
  });
}

export async function fetchTemplateRules(token: string): Promise<TemplateRule[]> {
  return apiRequest<TemplateRule[]>("/templates/rules", { method: "GET", token });
}

export async function createTemplateRule(
  token: string,
  payload: TemplateRulePayload,
): Promise<TemplateRule> {
  return apiRequest<TemplateRule>("/templates/rules", { method: "POST", token, body: payload });
}

export async function updateTemplateRule(
  token: string,
  ruleId: number,
  payload: Partial<TemplateRulePayload>,
): Promise<TemplateRule> {
  return apiRequest<TemplateRule>(`/templates/rules/${ruleId}`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export async function deleteTemplateRule(token: string, ruleId: number): Promise<void> {
  await apiRequest(`/templates/rules/${ruleId}`, { method: "DELETE", token });
}

export async function previewTemplateRule(
  token: string,
  payload: TemplatePreviewPayload,
): Promise<TemplatePreview> {
  return apiRequest<TemplatePreview>("/templates/rules/preview", {
    method: "POST",
    token,
    body: payload,
  });
}
