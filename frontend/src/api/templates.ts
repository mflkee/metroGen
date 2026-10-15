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
  drives_protocol: boolean;
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
  structure: FormStructure;
  overlay: FormStructure;
  overlay_keys: string[];
  problems: string[];
};

export type StructureColumn = { id: string; title?: string };
export type StructureRow = { id: string; kind?: string; at?: number; label?: string };
export type StructureBlock = {
  id: string;
  type: string;
  text?: string;
  columns?: StructureColumn[];
  rows?: StructureRow[];
};
export type StructureSection = { id: string; title?: string; blocks?: StructureBlock[] };
export type FormStructure = { schema?: number; sections?: StructureSection[] };

export type TemplateVersion = {
  revision: number;
  comment: string | null;
  published_by: string | null;
  published_at: string | null;
  overlay: FormStructure;
  structure_resolved: FormStructure;
};

export type TemplateCompareRequest = {
  other_code?: string | null;
  left_revision?: number | null;
  right_revision?: number | null;
};

export type TemplateDifference = {
  path: string;
  kind: string;
  before?: unknown;
  after?: unknown;
};

export type TemplateCompare = {
  left_label: string;
  right_label: string;
  differences: TemplateDifference[];
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

export async function saveFormDraft(
  token: string,
  code: string,
  payload: { structure?: FormStructure; overlay?: FormStructure; renderer?: string },
): Promise<TemplateFormDetail> {
  return apiRequest<TemplateFormDetail>(`/templates/${encodeURIComponent(code)}/draft`, {
    method: "PUT",
    token,
    body: payload,
  });
}

export async function publishForm(
  token: string,
  code: string,
  comment: string | null,
): Promise<TemplateVersion> {
  return apiRequest<TemplateVersion>(`/templates/${encodeURIComponent(code)}/publish`, {
    method: "POST",
    token,
    body: { comment },
  });
}

export async function fetchFormVersions(
  token: string,
  code: string,
): Promise<TemplateVersion[]> {
  return apiRequest<TemplateVersion[]>(`/templates/${encodeURIComponent(code)}/versions`, {
    method: "GET",
    token,
  });
}

export async function restoreFormVersion(
  token: string,
  code: string,
  revision: number,
): Promise<TemplateVersion> {
  return apiRequest<TemplateVersion>(
    `/templates/${encodeURIComponent(code)}/versions/${revision}/restore`,
    { method: "POST", token },
  );
}

export async function previewForm(token: string, code: string): Promise<string> {
  const result = await apiRequest<{ html: string }>(
    `/templates/${encodeURIComponent(code)}/preview`,
    { method: "POST", token },
  );
  return result.html;
}

export async function compareForms(
  token: string,
  code: string,
  payload: TemplateCompareRequest,
): Promise<TemplateCompare> {
  return apiRequest<TemplateCompare>(`/templates/${encodeURIComponent(code)}/compare`, {
    method: "POST",
    token,
    body: payload,
  });
}
