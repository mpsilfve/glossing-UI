'use strict';

class Legend extends React.Component {
    render() {
        return (
            <div id="legend">
                <h3>Table Legend</h3>
                <p className="input_token">Input token</p>
                {this.props.hasSeg &&   <div>
                                            <p className="preferred_segmentation"> Preferred segmentation</p>
                                            <p id="segmentation_list_legend">
                                                List of n-best segmentations
                                            </p>
                                        </div>}
                {this.props.hasGloss && <div>
                                            <p className="preferred_segmentation"> Preferred gloss</p>
                                            <p id="segmentation_list_legend">
                                                List of n-best glosses
                                            </p>
                                        </div>}
                
            </div>
        )
    }
}