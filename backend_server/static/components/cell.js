'use strict';

class Cell extends React.Component {
    constructor(props){
        super(props);

        this.state = {
        //   location: this.initilizeList(),
        }
    }

    // generate a list of gloss/seg predictions for rendering in a dropdown
    static getListForDropdown(token, modelType) {
        const prediction_list = token[modelType];
        let dropdown_list = [];
        for (let i = 0; i < prediction_list.length; i++) {
            const option = {
                id: i,
                title: prediction_list[i],
                selected: false,
                key: 'location'
            };
            dropdown_list.push(option);
        }

        const option = {
            id: prediction_list.length,
            title: "Custom",
            selected: false,
            key: 'location'
        };
        dropdown_list.push(option);

        return dropdown_list;
    }

    // update the state when the token segmentation lists get updated
    static getDerivedStateFromProps(nextProps) {
        const {token, hasSeg, hasGloss, index} = nextProps;

        let gloss_dropdown = [];
        if (hasGloss) {
            const gloss_list = token['gloss'];
            
            for (let i = 0; i < gloss_list.length; i++) {
                const option = {
                    id: i,
                    title: gloss_list[i],
                    selected: false,
                    key: 'gloss_location'
                };
                gloss_dropdown.push(option);
            }

            const option = {
                id: gloss_list.length,
                title: "Custom",
                selected: false,
                key: 'gloss_location'
            };
            gloss_dropdown.push(option);
        }
        
        let seg_dropdown = [];
        if (hasSeg) {
            const seg_list = token['segmentation'];

            for (let i = 0; i < seg_list.length; i++) {
                const glossOption = {
                    id: i,
                    title: seg_list[i],
                    selected: false,
                    key: 'location'
                };
                seg_dropdown.push(glossOption);
            }

            const segOption = {
                id: seg_list.length,
                title: "Custom",
                selected: false,
                key: 'location'
            };
            seg_dropdown.push(segOption);
        }
        
        return { location: seg_dropdown, gloss_location: gloss_dropdown };
    }

    // initilizeList() {
    //     // console.log(`this: ${this} props: `, this.props);
    //     const segmentation_list = this.props.token["segmentation"];
    //     let dropdown_list = [];
    //     for (let i = 0; i < segmentation_list.length; i++) {
    //         const option = {
    //             id: i,
    //             title: segmentation_list[i],
    //             selected: false,
    //             key: 'location'
    //         };
    //         dropdown_list.push(option);
    //     }

    //     const option = {
    //         id: segmentation_list.length,
    //         title: "Custom",
    //         selected: false,
    //         key: 'location'
    //     };
    //     dropdown_list.push(option);

    //     return dropdown_list;
    // }

    // update preferred segmentation
    changeList(modelType, newPreferred, isCustom, update_mode) {
        this.props.updatePreferredSegmentation(this.props.index, modelType, newPreferred, isCustom, update_mode);
    }

    resetThenSet = (id, key) => {
        const temp = [...this.state[key]];
      
        temp.forEach((item) => item.selected = false);
        temp[id].selected = true;
      
        this.setState({
          [key]: temp,
        });
    }


    render() {
        let sentence_message = '';
        if (this.props.show_sentence_number) {
            if ('annotation_id' in this.props.token) {
                sentence_message = `Annotation ${this.props.token.annotation_id}`
            } else {
                sentence_message = `Sentence ${this.props.token.sentence_id}`;
            }
        }

        return (
            <div className="cell">
                {/* &nbsp non-breaking space - at this space words are not broken and also the browser does not cancel it.
                Here, it is used for alignment. */}
                <p className='annotation'>{sentence_message}&nbsp;</p>
                <p className='input_token'>{this.props.token["input"]}</p>
                {this.props.hasSeg && <div>
                                        <p>{this.props.token["preferred_segmentation"]}</p>
                                        <Dropdown  
                                            title={this.props.token["preferred_segmentation"]}
                                            list={this.state.location}
                                            resetThenSet={this.resetThenSet}
                                            changeList = {(newPreferred, isCustom, mode) => this.changeList('segmentation', newPreferred, isCustom, mode)}
                                        />
                                       </div>}
                {this.props.hasGloss && <div>
                                            <p>{this.props.token["preferred_gloss"]}</p>
                                            <Dropdown 
                                                title={this.props.token["preferred_gloss"]}
                                                list={this.state.gloss_location}
                                                resetThenSet={this.resetThenSet}
                                                changeList={(newPreferred, isCustom, mode) => this.changeList('gloss', newPreferred, isCustom, mode)}
                                            />
                                        </div>}
            </div>
        )
    }
}