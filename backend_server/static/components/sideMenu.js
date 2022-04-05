'use strict';

class SideMenu extends React.Component {
    render() {
        // if the data comes from an ELAN file, enable saving as an .eaf file
        let is_eaf = (this.props.data[0].annotations_included.length > 0); 
        console.log(this.props.data);
        console.log(is_eaf);

        return (
            <div className="range_and_save">
                <Legend 
                    hasSeg={this.props.hasSeg}
                    hasGloss={this.props.hasGloss}
                />
                <PageTable 
                    data={this.props.data}
                    currPage={this.props.currPage}
                    onClick={(lower_b, upper_b, i) => this.props.onClick(lower_b, upper_b, i)}
                    onRetrieveSentence={(sentence_id) => {this.props.onRetrieveSentence(sentence_id)}}
                />
                <SaveMenu 
                    hasSeg={this.props.hasSeg}
                    hasGloss={this.props.hasGloss}
                    handleSave={(filename, format, saveGloss, saveSeg) => this.props.handleSave(filename, format, saveGloss, saveSeg)}
                    is_eaf={is_eaf}
                />
            </div>

        );
    }
};