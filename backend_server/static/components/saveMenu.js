'use strict';

class SaveMenu extends React.Component {
    constructor(props) {
        super(props);

        // keep track of the file saving options
        this.changeFilename = this.changeFilename.bind(this);
        this.changeFormat = this.changeFormat.bind(this);
        this.changeModelSave = this.changeModelSave.bind(this);

        this.state = {
            defaultFilename: "model_results",
            filename: "model_results",
            format: "txt",
            saveGloss: this.props.hasGloss,
            saveSeg: this.props.hasSeg
        };
    }

    changeFilename(e) {
        this.setState({filename: e.target.value});
    }

    changeFormat(e) {
        this.setState({format: e.target.value});
    }

    changeModelSave(e) {
        if (e.target.value === 'seg') {
            this.setState({saveGloss: false, saveSeg: true});
        } else if (e.target.value === 'gloss') {
            this.setState({saveGloss: true, saveSeg: false});
        } else {
            this.setState({saveGloss: true, saveSeg: true});
        }
    }

    onClick() {
        return this.props.handleSave(this.state.filename, this.state.format, this.state.saveGloss, this.state.saveSeg);
    }

    render() {
        const bothDefault = this.props.hasSeg && this.props.hasGloss;
        const segDefault = this.props.hasSeg && !bothDefault;
        const glossDefault = !bothDefault && !segDefault;

        return (
            <div id="save_menu">
                <p>Save results to desktop</p>

                <div id="file_format_buttons" className="form" onChange={this.changeFormat}>
                    <input type="radio" id="save_text_file" name="file_format" value="txt" defaultChecked/> Text
                    <input type="radio" id="save_eaf_file" name="file_format" value="eaf" disabled={!this.props.is_eaf} /> ELAN
                </div>

                <div id="model_save_buttons" className="form" onChange={this.changeModelSave}>
                    {this.props.hasSeg && <div>
                        <label className="option_radio_button">
                            <input type="radio" id="save_seg" name="model_to_save" value="seg" defaultChecked={segDefault}/> 
                            Only segmentation
                        </label>
                    </div>}
                    {this.props.hasGloss && <div>
                        <label className="option_radio_button">
                            <input type="radio" id="save_gloss" name="model_to_save" value="gloss" defaultChecked={glossDefault}/> 
                            Only gloss
                        </label>
                    </div>}
                    {this.props.hasSeg && this.props.hasGloss && <div>
                        <label className="option_radio_button">
                            <input type="radio" id="save_both" name="model_to_save" value="both" defaultChecked={bothDefault}/> 
                            Both
                        </label>
                    </div>}
                    
                </div>

                <input 
                    defaultValue={this.state.defaultFilename}
                    onChange={this.changeFilename}
                />

                <button id="save_changes_button" className="job_buttons" onClick={() => this.onClick()}>
                    Save changes
                </button>

            </div>  
        );
    }
}
