import React, {FC} from "react";
import {Grid, makeStyles} from "@material-ui/core";
import type {Theme} from 'src/theme';
import ActionPanel from "./ActionPanel";
import DeviceList from "./DeviceList";


interface Props {
    className?: string;
}

const useStyles = makeStyles((theme: Theme) => ({
    root: {}
}));

const Scanner: FC<Props> = ({className, ...rest}) => {
    const classes = useStyles();

    return (
        <Grid
            className={classes.root}
            container
            spacing={3}
            {...rest}
        >
            <Grid
                item
                lg={12}
                md={12}
                xl={12}
                xs={12}
            >
                <ActionPanel/>
            </Grid>
            <Grid
                item
                lg={12}
                md={12}
                xl={12}
                xs={12}
            >
                <DeviceList/>
            </Grid>
        </Grid>
    );
}

export default Scanner
