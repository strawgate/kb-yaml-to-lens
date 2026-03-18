"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/azure_openai/kibana/dashboard/azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3.json`."""
    assert integrations_yaml_for(
        'packages/azure_openai/kibana/dashboard/azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3.json'
    ) == snapshot("""\
dashboards:
- name: '[Azure OpenAI] Overview'
  id: azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: cf955ef2-c987-f646-9cb4-cba112d00bb6
    label: Subscriptions
    type: options
    field: azure.subscription_id
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: ccc608e1-0d73-02a1-ba0f-3601e328f1ca
    label: Resource Group
    type: options
    field: azure.resource.group
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: 179ea6c2-9e55-343b-90dd-8a6712d5f346
    label: Resource Name
    type: options
    field: azure.resource.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: a742531f-2d61-4eca-b069-74ece964034a
    title: Azure OpenAI Link
    hide_title: true
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: 9dae4891-8878-42f2-b429-593d71aae2b1, label: Azure OpenAI Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_9dae4891-8878-42f2-b429-593d71aae2b1_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 68ffd5fb-7aa9-4ccd-acfd-14fcafb021c8, label: Azure OpenAI PTU \n\
          Deployments, dashboard: \n\
          TODO_dashboard_id_for_link_68ffd5fb-7aa9-4ccd-acfd-14fcafb021c8_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 8a0a1521-1b26-43dd-81ff-2804312342bd, label: Azure OpenAI Billing, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_8a0a1521-1b26-43dd-81ff-2804312342bd_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 06d115b9-c21d-4fb1-b643-499f33b9add2, label: Azure OpenAI Content \n\
          Filtering Overview, dashboard: \n\
          TODO_dashboard_id_for_link_06d115b9-c21d-4fb1-b643-499f33b9add2_dashboard,
        new_tab: false, with_time: true, with_filters: false}
  - id: 55ea58ac-730f-4301-80ff-27b30f98b268
    title: ''
    size: {w: 18, h: 12}
    position: {x: 0, y: 4}
    markdown: {content: "# Azure OpenAI\\n\\nPrimary metrics from Azure's OpenAI service.
        This dashboard contains: \\n\\n- Request rates\\n- Error rates\\n- Token usage\\n\\
        - Chat completion latency", font_size: 12, links_in_new_tab: false}
  - id: 6f9d228a-b56a-411c-9153-08f4f8f04037
    title: ''
    hide_title: true
    description: Number of calls made to the Azure OpenAI API over a period of \n\
      time. Applies to PTU, PTU-Managed and Pay-as-you-go deployments.
    size: {w: 7, h: 6}
    position: {x: 18, y: 4}
    lens:
      id: c6201e5a-31be-3117-897b-ddcb17a04b31
      type: metric
      data_view: logs-*
      primary:
        id: 8de6ee90-1d28-5d3a-5c23-29db9ca081a8
        label: Total requests
        format: {type: number, decimals: 2, compact: true}
        formula: "count(kql='azure.open_ai.category : \\"RequestResponse\\" ')"
  - id: e99d4e71-252b-45f7-a3e6-bf627347f683
    title: ''
    hide_title: true
    description: Total token usage(input+output).
    size: {w: 7, h: 6}
    position: {x: 25, y: 4}
    lens:
      id: cc26119b-65d4-c995-6699-9c49e40fbc45
      type: metric
      data_view: metrics-*
      primary:
        id: 86e10925-759e-8fa9-a94c-cdcd921ec6c8
        label: Total tokens
        format: {type: number, decimals: 2, compact: true}
        aggregation: sum
        field: azure.open_ai.token_transaction.total
  - id: 5a0e50a9-2768-47c0-81b7-0c33361f3dd5
    title: Model usage
    description: Top 10 model usage.
    size: {w: 16, h: 12}
    position: {x: 32, y: 4}
    lens:
      id: a9cd0a48-0e9c-c737-9c7b-138803a5d1a9
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: 45862133-3a58-d112-d754-dfbd3642a4e4, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 1c3524e7-bd5e-718e-2dbc-804526597c68, type: values, size: 10, field: \n\
          azure.open_ai.properties.model_deployment_name}
  - id: eb83f647-b149-4510-92f1-3a87ff664ee1
    title: ''
    hide_title: true
    description: Total number of calls with error response (HTTP response code \n\
      4xx or 5xx).
    size: {w: 7, h: 6}
    position: {x: 18, y: 10}
    lens:
      id: 761bf086-ceab-1eab-dc1f-e7196c134ca0
      type: metric
      data_view: logs-*
      primary: {id: 4d28428b-5042-7353-430e-a25dafe9c296, label: Total errors, \n\
          formula: "count(kql='azure.open_ai.result_signature >= 400 and azure.open_ai.category
          : \\"RequestResponse\\" ')"}
  - id: 2091414b-fbae-451e-8e2a-c7d506f198db
    title: Overall request rate - by model deployment
    description: The overall requests count group by deployed model overtime.
    size: {w: 24, h: 16}
    position: {x: 0, y: 16}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: c46e93e3-382b-238f-67a7-d7b30f212ccf, label: Requests, aggregation: \n\
          sum, field: azure.open_ai.requests.total}
      breakdown: {id: cca1084f-576f-3a61-b364-e50d66b2a307, type: values, size: \n\
          20, field: azure.dimensions.model_deployment_name}
      id: c06ebe7d-847c-40f5-13aa-81738acf2878
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 6fe0e882-52a8-426f-ab07-3829bff17393
    title: Overall error rate - by response code
    description: The overall errors count group by error response code over \n\
      time.
    size: {w: 24, h: 16}
    position: {x: 24, y: 16}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 73002e1d-b7cd-0cf2-26c2-bfb812dcc4ca
        label: Errors
        filter: {kql: 'azure.open_ai.category : "RequestResponse" and azure.open_ai.result_signature
            >=400'}
        aggregation: count
        field: ___records___
      breakdown: {id: c77a3359-1595-2ef1-f076-c357d89b112d, type: values, size: \n\
          20, field: azure.open_ai.result_signature}
      id: 681af99c-5da9-ffe3-bebd-476fa3d29c28
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 980a4a83-bd69-4a1b-8264-3c5f865c545a
    title: Token usage
    description: Processed prompt token (input) and Generated completion token \n\
      (output).
    size: {w: 24, h: 16}
    position: {x: 0, y: 32}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 27f7c2ce-ac29-5c7e-320e-542d12e48387, label: Processed prompt \n\
          tokens, aggregation: sum, field: \n\
          azure.open_ai.processed_prompt_tokens.total}
      - {id: a282c43b-492a-b1b2-f744-e38d2a37e28c, label: Generated completion \n\
          tokens, aggregation: sum, field: azure.open_ai.generated_tokens.total}
      id: f3f655b4-818e-8b4a-d8de-f468e4b47089
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tokens}
      mode: stacked
  - id: df4e0f6a-2914-4fb7-b25a-4466a84b3b1a
    title: Chat completion latency - by model
    description: The chat completion latency in milliseconds group by model. \n\
      This includes only the chat completion latency and ignores the image model
      latency.
    size: {w: 24, h: 16}
    position: {x: 24, y: 32}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 8aa0536e-6e1c-4107-6bc8-2eef784a70b4, label: 'Response time / ms ', \n\
          formula: \n\
          (average(azure.open_ai.properties.response_time)-average(azure.open_ai.properties.request_time))/10000}
      breakdown: {id: 6122303b-def1-30a9-069d-13cb68a0f6f4, type: values, size: \n\
          20, field: azure.open_ai.properties.model_deployment_name}
      id: 68701c29-f4d2-7580-9aa9-8961e8d682f9
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 7599e392-ef0a-4a12-85bd-627ad65d6322
    title: Logs
    description: The actual ingested document data for detailed analysis.
    size: {w: 48, h: 18}
    position: {x: 0, y: 48}
    search: {saved_search_id: TODO_saved_search_id}
""")
