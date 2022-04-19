export interface Type {
    readonly id: number;
    name: 'miner' | 'exhaust' | 'recirc' | 'heater' | 'other' | string;
    label: string;
}

export type AutoResetAttr =
    'autoReset' |
    'thresholdLow' |
    'thresholdHigh' |
    'maxAttemptsLow' |
    'maxAttemptsHigh' |
    'attemptsLow' |
    'attemptsHigh' |
    'resetDelayLow' |
    'resetDelayHigh' |
    'timeOffLow' |
    'timeOffHigh' |
    'timeBeforeResetLow' |
    'timeBeforeResetHigh' |
    'postStateLow' |
    'postStateHigh'

export type MinerAttr =
    'id' |
    'type' |
    'label' |
    'notes' |
    'status' |
    'warning' |
    'total' |
    'lastOnTime' |
    AutoResetAttr

export interface AutoRest {
    // Auto restart
    autoReset: boolean;

    thresholdLow: number;
    thresholdHigh: number;

    maxAttemptsLow: number;
    maxAttemptsHigh: number;
    attemptsLow: number;
    attemptsHigh: number;

    resetDelayLow: number;
    resetDelayHigh: number;

    timeOffLow: number;
    timeOffHigh: number;

    timeBeforeResetLow: number;
    timeBeforeResetHigh: number;

    postStateLow: boolean;
    postStateHigh: boolean;
}

export interface Miner extends AutoRest {
    // Info
    readonly id: number;
    type: number;
    label: string;
    notes: string;

    // Indicator
    status: boolean;
    warning: boolean;

    // Utility Feature
    total: number;
    lastOnTime: string;

    // Option, for merge influxdb & backend
    curCons?: number;
    devices?: string[];
}

