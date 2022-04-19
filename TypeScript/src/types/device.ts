import {AutoRest} from "./miner";

export interface Device {
    readonly id: number;
    readonly mac: string;
    readonly ip: string;
    readonly isOnline: boolean;
    readonly addTime: string;
    readonly updateTime: string;
    readonly model: string;
    isBlink: boolean
    ports: number[];
}

export interface DeviceModel extends AutoRest {
    readonly id: number;
    name: string;
}

export interface Status {
    readonly name;
    readonly label;
    readonly value;
    readonly updateTime;
}
