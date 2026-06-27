export type ServiceAction =
  | 'list_due'
  | 'create_task'
  | 'update_task'
  | 'delete_task'
  | 'complete_occurrence'
  | 'get_task'
  | 'list_users';

export interface ServiceRequest {
  id: string;
  action: ServiceAction;
  params?: Record<string, unknown>;
}

export interface ServiceResponse {
  id: string;
  status: 'ok' | 'error';
  data?: Record<string, unknown>;
  error?: string;
}

export interface HomeAssistantLike {
  callService?: (domain: string, service: string, payload: Record<string, unknown>) => Promise<unknown>;
}

declare global {
  interface Window {
    hass?: HomeAssistantLike;
  }
}

export async function request(action: ServiceAction, params?: Record<string, unknown>): Promise<ServiceResponse> {
  const id = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
  const payload = { id, action, params };

  return new Promise((resolve, reject) => {
    const handler = (event: Event) => {
      const customEvent = event as CustomEvent<ServiceResponse>;
      if (customEvent.detail?.id !== id) {
        return;
      }

      window.removeEventListener('ha-event-todo_response', handler as EventListener);
      if (customEvent.detail.status === 'error') {
        reject(new Error(customEvent.detail.error || 'Unknown error'));
        return;
      }
      resolve(customEvent.detail);
    };

    window.addEventListener('ha-event-todo_response', handler as EventListener);

    if (window.hass?.callService) {
      window.hass.callService('todo_system', 'request', payload).catch((error) => {
        window.removeEventListener('ha-event-todo_response', handler as EventListener);
        reject(error);
      });
      return;
    }

    window.dispatchEvent(new CustomEvent('ha-event-todo_response', {
      detail: {
        id,
        status: 'ok',
        data: { occurrences: [], users: [] }
      }
    }));
  });
}
