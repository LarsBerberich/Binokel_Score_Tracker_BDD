/**
 * Dünner fetch-basierter API-Client für den Binokel Score Tracker.
 *
 * Basis-URL ist relativ (`/api`) → Same-Origin (ADR-010). Im Dev-Server
 * proxied Vite `/api` an das lokale Django (siehe vite.config.ts, TASK-007.8).
 *
 * Vertrag: frontend/openapi/binokel-api.v1.yaml
 */
import type {
  Health,
  Punktestaende,
  RundeErgebnis,
  RundeRequest,
  Spiel,
  SpielAnlegenRequest,
  SiegerErgebnis,
} from './types'

/** Relative Basis für alle API-Routen (Same-Origin). */
const API_BASE = '/api'

/** Fehler mit HTTP-Status und der vom Backend gelieferten Meldung. */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      headers: { Accept: 'application/json', ...(init?.body ? { 'Content-Type': 'application/json' } : {}) },
      ...init,
    })
  } catch {
    throw new ApiError(0, 'Netzwerkfehler: Server nicht erreichbar.')
  }

  const text = await response.text()
  const data = text ? JSON.parse(text) : undefined

  if (!response.ok) {
    const message =
      data && typeof data.fehler === 'string'
        ? data.fehler
        : `HTTP ${response.status}`
    throw new ApiError(response.status, message)
  }

  return data as T
}

function jsonBody(body: unknown): RequestInit {
  return { method: 'POST', body: JSON.stringify(body) }
}

// ── Slice 1: Spiel ────────────────────────────────────────────────────────────

export function spielAnlegen(body: SpielAnlegenRequest): Promise<Spiel> {
  return request<Spiel>(`${API_BASE}/spiele/`, jsonBody(body))
}

export function spielLaden(spielId: number): Promise<Spiel> {
  return request<Spiel>(`${API_BASE}/spiele/${spielId}/`)
}

// ── Slices 2–5: Runde ─────────────────────────────────────────────────────────

export function rundeAuswerten(
  spielId: number,
  body: RundeRequest,
): Promise<RundeErgebnis> {
  return request<RundeErgebnis>(`${API_BASE}/spiele/${spielId}/runden/`, jsonBody(body))
}

// ── Slice 6: Auswertung ───────────────────────────────────────────────────────

export function punktestaendeLaden(spielId: number): Promise<Punktestaende> {
  return request<Punktestaende>(`${API_BASE}/spiele/${spielId}/punktestaende/`)
}

export function siegerErmitteln(
  spielId: number,
  exakteStichwerte?: string,
): Promise<SiegerErgebnis> {
  const query = exakteStichwerte
    ? `?exakte_stichwerte=${encodeURIComponent(exakteStichwerte)}`
    : ''
  return request<SiegerErgebnis>(`${API_BASE}/spiele/${spielId}/sieger/${query}`)
}

// ── System ────────────────────────────────────────────────────────────────────

export function healthcheck(): Promise<Health> {
  return request<Health>('/health/')
}
