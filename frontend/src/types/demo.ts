import type { TravelEvent } from './api';

export const DEMO_EVENT: TravelEvent = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  event_type: 'flight_cancelled',
  timestamp: new Date().toISOString(),
  booking_ref: 'MUN-2025-8842',
  flight: {
    number: 'UA 2381',
    origin: 'SFO',
    destination: 'JFK',
    scheduled_departure: '2025-02-12T14:30:00+00:00',
    status: 'cancelled',
    reason: 'Mechanical issue — aircraft grounded',
    original_price: 400.0,
  },
  traveler: {
    id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    name: 'Sarah Chen',
    email: 'sarah@designpartner.com',
    role: 'VP Engineering',
    policy_tier: 'executive',
    slack_id: '@sarah.chen',
    timezone: 'America/Los_Angeles',
    calendar_integration: true,
    preferences: {
      seat: 'aisle',
      meal: 'vegetarian',
      airline_loyalty: 'United MileagePlus Gold',
    },
  },
  metadata: {},
};
