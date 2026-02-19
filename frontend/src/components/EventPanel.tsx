'use client';

import { useDashboard } from '@/context/DashboardContext';
import { Card } from '@/components/ui/Card';
import { TeamsPreview } from '@/components/TeamsPreview';

const STATUS_BADGES: Record<string, { bg: string; text: string; label: string }> = {
  proposed: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'PROPOSED' },
  confirmed: { bg: 'bg-green-100', text: 'text-green-700', label: 'BOOKED' },
  rejected: { bg: 'bg-red-100', text: 'text-red-700', label: 'REJECTED' },
  escalated: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'ESCALATED TO HUMAN' },
};

export function EventPanel() {
  const { state, respondToEvent } = useDashboard();
  const event = state.currentEvent;
  const resolution = state.resolution;

  const badge = resolution ? STATUS_BADGES[resolution.status] : null;

  return (
    <div className="flex h-full w-full flex-col gap-3 overflow-y-auto">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Disruption Event
      </h2>

      {!event ? (
        <Card className="flex flex-1 items-center justify-center">
          <p className="text-sm text-gray-400">
            No active event. Click &ldquo;Trigger Demo Event&rdquo; to start.
          </p>
        </Card>
      ) : (
        <>
          <Card>
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                {event.event_type.replace('_', ' ').toUpperCase()}
              </span>
              <span className="font-mono text-xs text-gray-500">{event.booking_ref}</span>
            </div>

            {event.flight && (
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Flight</span>
                  <span className="font-mono font-medium text-gray-900">{event.flight.number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Route</span>
                  <span className="font-medium text-gray-900">
                    {event.flight.origin} → {event.flight.destination}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Departure</span>
                  <span className="font-mono text-xs text-gray-700">
                    {new Date(event.flight.scheduled_departure).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  <span className="font-medium text-red-600">{event.flight.status}</span>
                </div>
                {event.flight.reason && (
                  <p className="mt-1 text-xs text-gray-500">{event.flight.reason}</p>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Original Price</span>
                  <span className="font-mono text-gray-900">${event.flight.original_price.toFixed(2)}</span>
                </div>
              </div>
            )}
          </Card>

          <Card>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
              Traveler
            </h3>
            <div className="space-y-1.5 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Name</span>
                <span className="font-medium text-gray-900">{event.traveler.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Role</span>
                <span className="text-gray-700">{event.traveler.role}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Policy Tier</span>
                <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                  {event.traveler.policy_tier}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Email</span>
                <span className="font-mono text-xs text-gray-700">{event.traveler.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Teams</span>
                <span className="font-mono text-xs text-gray-700">{event.traveler.messaging_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Calendar</span>
                <span className="text-gray-700">{event.traveler.calendar_integration ? 'Linked' : 'Not linked'}</span>
              </div>
            </div>
          </Card>

          {resolution && (
            <Card>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
                Resolution
              </h3>
              <div className="space-y-1.5 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  {badge && (
                    <span
                      className={`rounded ${badge.bg} px-2 py-0.5 text-xs font-medium ${badge.text}`}
                    >
                      {badge.label}
                    </span>
                  )}
                </div>
                {resolution.chosen_option && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Rebooked</span>
                      <span className="font-mono font-medium text-gray-900">
                        {resolution.chosen_option.flight}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">New Price</span>
                      <span className="font-mono text-gray-900">
                        ${resolution.chosen_option.price.toFixed(2)}
                      </span>
                    </div>
                  </>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Agents</span>
                  <span className="text-gray-700">{resolution.agents_involved.length}</span>
                </div>

                {/* Response buttons — only when proposed */}
                {resolution.status === 'proposed' && (
                  <div className="flex w-full flex-col gap-2 pt-2 sm:flex-row">
                    <button
                      onClick={() => respondToEvent('confirm')}
                      disabled={state.isResponding}
                      className="min-h-[44px] flex-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-green-500 disabled:opacity-50"
                    >
                      {state.isResponding ? 'Processing...' : 'Confirm Booking'}
                    </button>
                    <button
                      onClick={() => respondToEvent('options')}
                      disabled={state.isResponding}
                      className="min-h-[44px] flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:opacity-50"
                    >
                      See Options
                    </button>
                  </div>
                )}

                {/* Escalation message */}
                {resolution.status === 'escalated' && (
                  <div className="mt-2 rounded-lg bg-amber-50 p-2.5 text-xs text-amber-700">
                    This resolution could not be handled automatically and has been escalated to a
                    human travel agent for review.
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Teams Preview — show comms message */}
          {resolution?.comms_result && (
            <TeamsPreview
              text={resolution.comms_result.text}
              teamsSent={resolution.comms_result.teams_sent}
            />
          )}
        </>
      )}
    </div>
  );
}
