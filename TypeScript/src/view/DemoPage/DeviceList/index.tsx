// Library
import React, {FC, useEffect, useState} from "react";
import clsx from "clsx";
import {useSnackbar} from "notistack";
import {makeStyles} from "@material-ui/core";
import {Button, Card, CardContent, CardHeader, CircularProgress, Divider, IconButton, Link} from "@mui/material";
import {
    Lightbulb as LightbulbIcon,
    LightbulbOutlined as LightbulbOutlinedIcon,
} from '@mui/icons-material/';
import {green, grey} from "@mui/material/colors";
import {DataGrid, GridRowsProp, GridColDef, GridToolbar} from '@mui/x-data-grid';
import {Empty} from "antd";

// Utils
import type {Theme} from 'src/theme';
import {Device} from "src/types/device";

// Store
import {useDispatch, useSelector} from "src/store";
import {getMiners} from "src/slices/miner";
import {getDevices, updateDevice} from "src/slices/device";

// Component
import Tooltip from "src/components/Tooltip";
import ModelApplyDialog from "./ModelApplyDialog";
import PortAssignDialog from "./PortAssignDialog";


interface Props {
    className?: string;
}

const useStyles = makeStyles((theme: Theme) => ({
    root: {}
}));

const DeviceList: FC<Props> = ({className, ...rest}) => {
    const classes = useStyles();
    const {enqueueSnackbar} = useSnackbar();
    const dispatch = useDispatch();
    const {device} = useSelector(state => state.device)
    const {setting} = useSelector(state => state.setting)
    const interval: number = Number(setting.byName['interval'].value) * 1000

    // Dialog for Apply MinerModel configuration to Device & Assign to Port
    const [openModelApply, setOpenModelApply] = useState<boolean>(false);
    const [openPortAssign, setOpenPortAssign] = useState<boolean>(false);

    // Apply default miner type on
    const [selectedRows, setSelectedRows] = React.useState<number[]>([]);

    const handleClickApplyConfig = () => {
        if (selectedRows.length > 0) {
            setOpenModelApply(true)
        } else {
            enqueueSnackbar('Please select device first', {
                variant: 'warning'
            });
        }
    }

    /**
     * While click "Assign" button and want to connect a device with a specific port
     * @param device
     */
    const handleClickAssign = (device: Device) => (event) => {
        // While click assign button, only make current row selected
        setSelectedRows([device.id])
        setOpenPortAssign(true)
    }

    /**
     * Send request to turn on Blink for miner
     * @param deviceId
     * @param isBlink
     */
    const handleClickBlink = (deviceId: number | string, isBlink: boolean) => {
        const newDevice: Device = {
            ...device.byId[deviceId],
            isBlink: isBlink
        }
        dispatch(updateDevice(newDevice))
    }

    const handleSectionModelChange = (newSelectedRows: number[]) => {
        setSelectedRows(newSelectedRows);
    }

    const handleClosePortAssign = () => {
        setOpenPortAssign(false);
    };

    const handleCloseModelApply = () => {
        setOpenModelApply(false)
    }

    const columns: GridColDef[] = [
        {field: 'mac', headerName: 'Mac Address', flex: 1,},
        {field: 'ip', headerName: 'IP Address', flex: 1,},
        {
            field: 'ports',
            headerName: 'Miner Port',
            flex: 1,
            renderCell: (params) => {
                return (params.value as number[]).map((minerId) => (
                    <Link href={`/app/miners/${minerId}`} key={minerId} margin={0.5}>{minerId}</Link>
                ))
            }
        },
        {field: 'model', headerName: 'Miner Model', flex: 1,},
        {
            field: 'isBlink',
            headerName: 'isBlink',
            flex: 1,
            renderCell: (params) => {
                if (true) {
                    return (
                        <>
                            <Button
                                sx={{margin: 2}}
                                size="small"
                                variant="contained"
                                startIcon={<CircularProgress size="1rem" color="secondary"/>}
                                onClick={() => handleClickBlink(params.id, false)}
                            >
                                Stop
                            </Button>
                        </>
                    )
                } else {
                    return (
                        <Button
                            sx={{margin: 2}}
                            size="small"
                            variant="contained"
                            onClick={() => handleClickBlink(params.id, false)}
                        >
                            Start
                        </Button>
                    )
                }

            }
        },
        {
            field: 'isOnline',
            headerName: 'isOnline',
            flex: 1,
            renderCell: (params) => {
                return (
                    params.value ? (
                        <LightbulbIcon sx={{color: green[500]}}/>
                    ) : (
                        <LightbulbOutlinedIcon sx={{color: grey[500]}}/>
                    )
                )
            }
        },
        {
            field: 'action',
            headerName: 'Action',
            flex: 1,
            renderCell: (params) => (
                <Tooltip title="Assign Device to Different Port">
                    <Button
                        variant="outlined"
                        onClick={handleClickAssign(params.row as Device)}
                    >
                        Assign
                    </Button>
                </Tooltip>
            )
        },
    ];

    useEffect(() => {
        dispatch(getDevices())
        dispatch(getMiners())
        const timer = setInterval(() => {
            dispatch(getDevices())
        }, interval);
        return () => clearInterval(timer)
    }, [dispatch, interval])

    if (device.allIds.length === 0) {
        return <Empty/>
    }

    const rows: GridRowsProp = Object.entries(device.byId).map(([k, v]: [string, Device]) => v)

    return (
        <Card
            className={clsx(classes.root, className)}
            {...rest}
        >
            <CardHeader
                title="Device List"
                action={
                    <Button onClick={handleClickApplyConfig}>
                        Apply Config
                    </Button>
                }
            />
            <Divider/>
            <CardContent>
                <ModelApplyDialog
                    selectedRows={selectedRows}
                    open={openModelApply}
                    handleClose={handleCloseModelApply}
                />
                <PortAssignDialog
                    deviceId={selectedRows[0]}
                    open={openPortAssign}
                    handleClose={handleClosePortAssign}
                />
                <div
                    style={{height: 600, width: '100%'}}
                >
                    <DataGrid
                        rows={rows}
                        columns={columns}
                        components={{Toolbar: GridToolbar}}
                        checkboxSelection
                        disableSelectionOnClick
                        selectionModel={selectedRows}
                        onSelectionModelChange={handleSectionModelChange}
                    />
                </div>
            </CardContent>
        </Card>
    );
}

export default DeviceList
