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

class Dropdown extends React.Component {
    constructor(props){
        super(props)
        this.state = {
          isListOpen: false,
          headerTitle: this.props.title,
          isCustom: false,
          value: '',
        //   set update_mode to default checked radio button value
          selected_update_mode: "only_this",
        };
        // from https://stackoverflow.com/questions/53846717/this-handlechange-this-handlechange-bindthis
        // In JavaScript, class methods are not bound by default. If you forget to bind this.handleClick and 
        // pass it to onClick, this will be undefined when the function is actually called.

        // This is not React-specific behavior; it is a part of how functions work in JavaScript. 
        // Generally, if you refer to a method without () after it, such as onClick={this.handleClick}, you should bind that method.
        
        // If calling bind annoys you, there are two ways you can get around this. you can use 
        // the experimental public class fields syntax or arrow functions in the callback
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleRadioChange = this.handleRadioChange.bind(this);
        this.handleCancel = this.handleCancel.bind(this);

    }

    //  when preferred segmentation changes, set the segmentation on dropdown list button to that.
    componentDidUpdate(prevProps) {
        if (prevProps.title !== this.props.title) {
            this.setState({
                title: this.props.title,
            });
        }
    }

    static getDerivedStateFromProps(nextProps) {
        const { list, title } = nextProps;
        const selectedItem = list.filter((item) => item.selected);
      
        if (selectedItem.length) {
          return {
            headerTitle: selectedItem[0].title,
          };
        }
        return { headerTitle: title };
    }

    toggleList = () => {
        this.setState(prevState => ({
          isListOpen: !prevState.isListOpen
       }))
    }

    // if custom option is selected, save the current title, so that
    // if the custom option is cancelled, we can returned to selecting
    // the previously selected item
    selectItem = (item) => {
        const { resetThenSet } = this.props;
        const { title, id, key } = item;
        const previousTitle = this.state.headerTitle;
        this.setState({
          headerTitle: title,
          isListOpen: false,
        }, () => resetThenSet(id, key));

        // perform update of segmentations
        if (item.title != "Custom") {
            this.props.changeList(item.title, false);
            this.setState(
                {
                    isCustom: false,
                }
            );
        } else {
            this.setState(
                {
                    isCustom: true,
                    previousTitle: previousTitle,
                }
            );
        }
    }

    handleChange(event) {
        this.setState({
            value: event.target.value,
        });
    }

    handleSubmit(event) {
        this.props.changeList(this.state.value, true, this.state.selected_update_mode);
        this.setState({
            value: '',
            isCustom: false,
        });
        event.preventDefault();
    }

    // in case if custom option is cancelled, the state is returned to default values
    // and the selection returns to the previous selected item, which title is stored
    // in previousTitle
    handleCancel(event) {
        this.setState({
            value: '',
            isCustom: false,
        });

        for (let i = 0; i < this.props.list.length; i++) {
            if (this.props.list[i].title === this.state.previousTitle) {
                this.selectItem(this.props.list[i]);
            }
        }
        event.preventDefault();

    }

    handleRadioChange(event) {
        let update_mode = "all";
        if (event.target.value == "only_this") {
            update_mode = "only_this";
            // alert("Only this option is chosen");
        } else if (event.target.value == "all_after") {
            update_mode = "all_after";
            // alert("All after option is chosen");
        } else {
            // alert("All option is chosen");
        }
        this.setState({
            selected_update_mode: update_mode,
        });
    }

    render() {
        const { isListOpen, headerTitle } = this.state;
        const { list } = this.props;

        return (
          <div className="dd-wrapper">
            <button
              type="button"
              className="dd-header"
              onClick={this.toggleList}
            >
              <div className="dd-header-title">{headerTitle}</div>
              {/* {isListOpen
                ? <FontAwesome name="angle-up" size="2x" />
                : <FontAwesome name="angle-down" size="2x" />} */}
            </button>
            {isListOpen && (
              <div
                role="list"
                className="dd-list"
              >
                {list.map((item) => (
                  <button
                    type="button"
                    className="dd-list-item"
                    key={item.id}
                    onClick={() => this.selectItem(item)}
                  >
                    {item.title}
                    {' '}
                    {/* {item.selected && <FontAwesome name="check" />} */}
                  </button>
                ))}
              </div>
              // add custom option if chosen
            )}
            {this.state.isCustom && (
                <form onSubmit={this.handleSubmit}>
                    <input 
                        type="text" 
                        value={this.state.value} 
                        onChange={this.handleChange} 
                        id="custom_segmentation_input"
                        required>
                    </input>
                    <div id="mode_buttons">
                        <input  type="radio" 
                                id="only_this" 
                                name="update_mode" 
                                value="only_this" 
                                checked={this.state.selected_update_mode === "only_this"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="only_this" className="mode_button">only this</label>
                        <input  type="radio" 
                                id="all_after" 
                                name="update_mode" 
                                value="all_after" 
                                checked={this.state.selected_update_mode === "all_after"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all_after" className="mode_button">all after</label>
                        <input  type="radio" 
                                id="all" 
                                name="update_mode" 
                                value="all"
                                checked={this.state.selected_update_mode === "all"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all" className="mode_button">all</label>
                    </div>
                    <input type="submit" value="Submit"></input>
                    <button onClick={this.handleCancel}>Cancel</button>
                </form>
            )}
          </div>
        )
      }
}


class ResultsTable extends React.Component {
    render() {
        let rows = [];
        const tokens_included = this.props.upper_bound - this.props.lower_bound + 1;
        const column_number = (tokens_included >= 8) ? 8 : tokens_included;
        const row_number = Math.ceil(tokens_included/10);

        let current_index = 0;
        // the outer loop will count up to (COL LENGTH = 8), and break if there is less
        // 
        for (let i = 0; i < row_number; i++) {
            let row = [];

            for (let j = 0; j < column_number; j++) {
                const current_token = current_index + this.props.lower_bound;
                if (current_token > this.props.upper_bound) {
                    break;
                }
                // TODO why does this render every time
                // console.log(`Lower bound is ${this.props.lower_bound} and current_index is ${current_index} and index is ${current_index + this.props.lower_bound}`)
                
                // assign class to cells based on sentence id to colour different sentences differently in styling
                // odd sentences will get className="odd", and even will get "even".
                let cell_sentence_class = 'odd';
                if (this.props.data[current_token].sentence_id % 2 === 0) {
                    cell_sentence_class = 'even';
                }

                let show_sentence_number = false;
                if (current_token === 0 || this.props.data[current_token].sentence_id != this.props.data[current_token - 1].sentence_id) {
                    show_sentence_number = true;
                }

                row.push(
                    <td key={j} className={cell_sentence_class}>
                        <Cell
                            token={this.props.data[current_token]}
                            show_sentence_number={show_sentence_number}
                            hasSeg={this.props.hasSeg}
                            hasGloss={this.props.hasGloss}
                            index={current_index + this.props.lower_bound}
                            updatePreferredSegmentation = {
                                ( index, modelType, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                            }
                        />
                    </td>
                )
                current_index++;
            }
            rows.push(
                <tr key={i}>
                    {row}
                </tr>
            )
        }
        
        return (
            <div className="results_wrapper">
                <table id="results_table">
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        )
    }
}

class DynamicResultsTable extends React.Component {
    render() {
        let rows = [];

        let current_index = this.props.lower_bound;
        while (current_index < this.props.upper_bound) {
            console.log('Current index');
            console.log(current_index);
            let row = [];
            let total_chars = 0;
            while (total_chars < 60 && row.length < 8) {

                if (current_index >= this.props.upper_bound+1) {
                    break;
                }

                // Color the cell blue or purple if it's in an even or odd sentence
                let cell_sentence_class = 'odd';
                if (this.props.data[current_index].sentence_id % 2 === 0) {
                    cell_sentence_class = 'even';
                }

                // If it's the first token in a sentence, show a sentence label
                let show_sentence_number = false;
                if (current_index === 0 || this.props.data[current_index].sentence_id != this.props.data[current_index - 1].sentence_id) {
                    show_sentence_number = true;
                }

                row.push(
                    <div key={current_index} className={cell_sentence_class}>
                        <Cell
                            token={this.props.data[current_index]}
                            show_sentence_number={show_sentence_number}
                            hasSeg={this.props.hasSeg}
                            hasGloss={this.props.hasGloss}
                            index={current_index}
                            updatePreferredSegmentation = {
                                ( index, modelType, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                            }
                        />
                    </div>
                )

                if (this.props.data[current_index].hasOwnProperty('preferred_gloss')) {
                    total_chars += this.props.data[current_index].preferred_gloss.length; 
                } else {
                    total_chars += this.props.data[current_index].preferred_segmentation.length;
                }
                current_index++;
            }

            // if there are less than four elements in the row, don't stretch
            const is_short_row = (row.length < 4);
            let filler = [];
            if (is_short_row) {
                filler = Array(8 - row.length).fill().map( () =>
                    {<div className="results_row_short_filler"></div>}
                );
            }

            rows.push(
                <div key={rows.length} className="results_flex_row">
                    {row}
                    {is_short_row && filler}
                </div>
            )
        }

        return (
            <div className="results_wrapper">
                <div id="results_grid">
                    {rows}
                </div>
            </div>
        )
    }
}

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

class PageTableCellButton extends React.Component {
    handleClick() {

    }

    render() {
        let display_type = (this.props.is_curr_page) ? "curr_page_range_button" : "range_button";
        return (
            <button 
                className={display_type}
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound, this.props.page_index)}
            >
                {this.props.lower_bound} - {this.props.upper_bound}
            </button>
        )
    }
}

class PageTableSentenceButton extends React.Component {
    render() {
        let message;
        if (this.props.annotation_id === null) {
            message = this.props.sentence_id;
        } else {
            message = this.props.annotation_id;
        }
     
        return (
            <button 
                onClick={() => {this.props.onClick(this.props.sentence_id)}}
                className="range_button"
            >
                {message}
            </button>
        )
    }
}


class PageTable extends React.Component {
    /**
     * Displays the results page table that allows to navigate between 
     * results pages (token ranges). 
     */

    constructor(props) {
        super(props);

        console.log(this.props.currPage);

        this.state = {
            sentences_included: this.props.data[0].sentences_included,
            annotations_included: this.props.data[0].annotations_included,
        };
    }

    onClick(lower_b, upper_b, i) {
        this.props.onClick(lower_b, upper_b, i);
        
        let currPage = this.props.currPage;
        this.setState({
            sentences_included: this.props.data[currPage].sentences_included,
            annotations_included: this.props.data[currPage].annotations_included,
        });
    }

    render() {
        const pages = this.props.data;
        let rows = [];
        for (let i = 0; i < pages.length; i++) {
            let is_curr_page = (i === this.props.currPage);
            rows.push(
                <tr key={i}>
                    <td>
                        <PageTableCellButton 
                            lower_bound={pages[i].first_token} 
                            upper_bound={pages[i].last_sentence_end}
                            page_index = {i}
                            is_curr_page = {is_curr_page}
                            onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                        />
                    </td>
                </tr>
            );
        }

        let annotation_present = false;
        let currPage = this.props.currPage;
        let sentences_included = this.props.data[currPage].sentences_included;
        let annotations_included = this.props.data[currPage].annotations_included;

        console.log(sentences_included.length);
        console.log(annotations_included.length);
        if (annotations_included.length === sentences_included.length) {
            annotation_present = true;
        }

        let sentence_rows = [];
        for (let j = 0; j < sentences_included.length; j++) {
            const annotation = annotation_present ? annotations_included[j] : null;
            // console.log(annotation);
            sentence_rows.push(
                <tr key={j}>
                    <td>
                        <PageTableSentenceButton 
                            sentence_id={sentences_included[j]}
                            annotation_id={annotation}
                            onClick={(sentence_id) => {this.props.onRetrieveSentence(sentence_id)}}
                        />
                    </td>
                </tr>
            );
        }

        const unit_type = annotation_present ? 'an annotation' : 'a sentence';

        return (
            <div id="range_table_wrapper">
             <table>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p>Select {unit_type} to modify:</p>
            <table>
                <tbody>
                    {sentence_rows}
                </tbody>
            </table>
            </div>
        )
    }
}


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


class PageStepButton extends React.Component {
    constructor(props) {
        super(props);

        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        let to_page;

        // find the previous/next page index (within bounds)
        if (this.props.direction === "prev") {
            to_page = Math.max(this.props.currPage - 1, 0);
        } else {
            to_page = Math.min(this.props.currPage + 1, this.props.pages.length - 1);
        }

        // pass up to PageNav
        let to_page_lower_bound = this.props.pages[to_page].first_token;
        let to_page_upper_bound = this.props.pages[to_page].last_sentence_end;

        return this.props.onClick(to_page_lower_bound, to_page_upper_bound, to_page);
    }

    render() {
        let display_text = (this.props.direction === "prev") ? "<-" : "->";
        
        return (
            <button
                className="range_button"
                onClick={this.onClick}
            >
                {display_text}
            </button>
        );
    }
}


class PageNavButton extends React.Component {
    render() {
        let display_type = (this.props.is_curr_page) ? "curr_page_range_button" : "range_button";
        return (
            <button 
                className={display_type}
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound, this.props.page_index)}
            >
                {this.props.page_index + 1}
            </button>
        )
    }
}


class PageNav extends React.Component {
    constructor(props) {
        super(props);
    }

    onClick(lower_b, upper_b, i) {
        this.props.onClick(lower_b, upper_b, i);
    }

    render() {
        const pages = this.props.data;
        let cols = [];

        // first, a prev button, then the page buttons, then a next button
        cols.push(
            <td key="prev">
                <PageStepButton
                    pages={pages}
                    direction="prev"
                    currPage={this.props.currPage}
                    onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                />
            </td>
        );

        for (let i=0; i<pages.length; i++) {
            let is_curr_page = (this.props.currPage === i);
            cols.push(
                <td key={i}>
                    <PageNavButton 
                            lower_bound={pages[i].first_token} 
                            upper_bound={pages[i].last_sentence_end}
                            page_index={i}
                            is_curr_page={is_curr_page}
                            onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                        />
                </td>
            );
        }

        cols.push(
            <td key="next">
                <PageStepButton
                    pages={pages}
                    direction="next"
                    currPage={this.props.currPage}
                    onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                />
            </td>
        );

        return (
            <div className="page_nav_wrapper">
                <table id="page_nav_table">
                    <tbody>
                        <tr>
                            {cols}
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}


class ResubmitSentenceSection extends React.Component {
    constructor(props){
        super(props)
        this.state = {
          value: this.props.sentence,
        //   set update_mode to default checked radio button value
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    // called upon sentence prop update
    componentDidUpdate(prevProps) {
        if (prevProps.sentence !== this.props.sentence) {
            this.setState({
                value: this.props.sentence,
            });
        }
    }

    handleChange(event) {
        this.setState({
            value: event.target.value,
        });
    }

    handleSubmit(event) {
        this.props.onSubmit(this.state.value);
        this.setState({
            value: '',
        });
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit} className="form">
                <input 
                    type="text" 
                    value={this.state.value}
                    onChange={this.handleChange}
                    className="user_input" 
                    id="modified_sentence_input"
                    required>
                </input>
                <input type="submit" 
                        className="job_buttons"
                        value="Re-submit sentence">
                </input>
                <button className="job_buttons"
                        onClick={this.props.cancelSentenceResubmission}>
                            Cancel
                </button>
            </form>
        );

    }
}

/*
Main React component, renders ResultsTable and SideMenu componenets.

Props: 
    data - list of tokens with inputs and segmentations
    jobId
*/
class ResultsSection extends React.Component {

    constructor(props) {
        super(props);
        const {pages, sentence_boundaries} = this.computePages(props.data);
        // make a dictionary {key: list of indixes} and store it in state
        // but also make it updatable?
        const token_dictionary = this.makeTokenDictionary(props.data);

        // display segmentation and/or gloss?
        const includeSeg = 'preferred_segmentation' in props.data[0];
        const includeGloss = 'preferred_gloss' in props.data[0];
        
        this.state = {
            hasSeg: includeSeg,
            hasGloss: includeGloss,
            //  initial lower and upper bound from the rows 2D array
            lower_bound: pages[0].first_token,
            upper_bound: pages[0].last_sentence_end,
            pages: pages,
            currPage: 0,
            // below is a copy of input data
            data: [...props.data],
            token_dictionary: token_dictionary,
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_boundaries,
        };

        this.cancelSentenceResubmission = this.cancelSentenceResubmission.bind(this);
    }

    componentDidUpdate(prevProps, prevState) {
        // if the page changes, then hide the input box that allows sentence resubmission, 
        // since the sentence is no longer visible.
        if (prevState.upper_bound !== this.state.upper_bound) {
            this.setState({
                modify_sentence: false,
            });
        }

        // TODO: come back here for page legend!
        // console.log(this.state);
    }

    cancelSentenceResubmission() {
        this.setState({
            modify_sentence:false,
        });
    }

    computePages(data) {
        let pages = [];
        const token_list = data;
        const token_number = token_list.length;

        // The token index at the start of the current row
        let first_token = 0;
        let last_sentence_end = 0;
        let current_sentence_id = token_list[0].sentence_id;

        let sentence_boundaries = {}
        sentence_boundaries[token_list[0].sentence_id] = 0;

        const max_tokens_per_view = 50;
        for (let i = 0; i < token_number; i++) {
            // if a new sentence starts, update the current_sentence_id and sentence start and end
            if (current_sentence_id != token_list[i].sentence_id) {
                last_sentence_end = i - 1;
                current_sentence_id = token_list[i]["sentence_id"];
                sentence_boundaries[current_sentence_id] = i;
            }

            // when you exceed max tokens, make it last_sentence_end
            if (i == token_number - 1) {
                last_sentence_end = i;
            }

            // if we exceed max tokens per view or are at the end of the token list
            // 
            if (i - first_token + 1 >= max_tokens_per_view || i == token_number - 1) {
                // if sentence is too long, that just make it the end, otherwise just use
                // the sentence end
                last_sentence_end = first_token >= last_sentence_end ? i : last_sentence_end;
                // console.log(sentence_start);
                // console.log(`Start: ${first_token} and end ${last_sentence_end}`);
                let sentences_included = [];
                sentences_included.push(token_list[first_token].sentence_id);
                // in case if we deal with eaf file, add annotation id
                let annotations_included = [];
                if ('annotation_id' in token_list[first_token]) {
                    annotations_included.push(token_list[first_token]['annotation_id']);
                }
                // console.log(sentences_included);
                // include sentences that are within the current view
                for (let key in sentence_boundaries) {
                    if (sentence_boundaries[key] > first_token && sentence_boundaries[key] <= last_sentence_end) {
                        // keys in JavaScript are strings, and we need integers so use Number()
                        sentences_included.push(Number(key));
                        if ('annotation_id' in token_list[sentence_boundaries[key]]) {
                            annotations_included.push(token_list[sentence_boundaries[key]]['annotation_id']);
                        }
                    }           
                }
                if (('annotation_id' in token_list[first_token]) && (sentences_included.length != annotations_included.length)) {
                    throw new Error('Annotations are present but sentences included are not equal to annotations included!');
                }
                let page = {first_token, last_sentence_end, sentences_included, annotations_included};
                pages.push(page);
                first_token = last_sentence_end + 1;
            }
        }
        return {pages, sentence_boundaries};
    }

    // make a dictionary {key: list of indixes} which stores the
    // indices the input occurs in token_list.
    makeTokenDictionary(token_list) {
        const token_number = token_list.length;
        let dictionary = {};
        let current_token;
        for (let i = 0; i < token_number; i++) {
            current_token = token_list[i];
            if (!(current_token.input in dictionary)) {
                dictionary[current_token.input] = [i];
            } else {
                dictionary[current_token.input].push(i);
            }
        }
        return dictionary;
    }


    // Here is the page change method!
    handleClick(lower_b, upper_b, i) {
        this.setState({
            lower_bound: lower_b,
            upper_bound: upper_b,
            currPage: i
        });
        // console.log('The ResultsSection handleClick method was called.');
    }

    // update preferred segmentation and segmentation lists based on update mode and 
    // whether it is custom.
    updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode) {
        // create keys based on modelType value
        const modelKey = modelType;
        const modelPreferredKey = 'preferred_' + modelType;
        
        // TODO do something with the update mode
        const newData = [...this.state.data];
        console.log(`The index is ${index}`);
        newData[index][modelPreferredKey] = newPreferred;
        
        if (isCustom === true) {
            const same_token_index_list = this.state.token_dictionary[newData[index].input];

            if (update_mode === "only_this") {
                console.log("only this");
                newData[index][modelKey].push(newPreferred);
            } else if (update_mode === "all_after") {
                console.log("all after");
                for (let i = 0; i < same_token_index_list.length; i++) {
                    console.log(`The current index is ${same_token_index_list[i]}`)
                    if (same_token_index_list[i] > index) {
                        console.log(`This index is pushed ${same_token_index_list[i]}`)
                        newData[same_token_index_list[i]][modelKey].push(newPreferred);
                        newData[same_token_index_list[i]][modelPreferredKey] = newPreferred;
                    }
                }
            } else if (update_mode === "all") {
                console.log("all");
                for (let i = 0; i < same_token_index_list.length; i++) {
                    newData[same_token_index_list[i]][modelKey].push(newPreferred);
                    newData[same_token_index_list[i]][modelPreferredKey] = newPreferred;
                }
            } else {
                console.log("Wrong update mode!")
            }
        }

        this.setState({
            data: newData,
        });
    }

    determineSentenceBoundaries(sentence_id) {
        const sentence_start = this.state.sentence_boundaries[sentence_id];
        let sentence_end;

        if (this.state.sentence_boundaries[sentence_id + 1]) {

            sentence_end = this.state.sentence_boundaries[sentence_id + 1] - 1;
        } else {
            sentence_end = this.state.data.length - 1;
        }

        return [sentence_start, sentence_end];
    }

    retrieveSentenceToModify(sentence_id) {
        const sentence_boundary = this.determineSentenceBoundaries(sentence_id);
        const sentence_start = sentence_boundary[0];
        const sentence_end = sentence_boundary[1];

        console.log(`start ${sentence_start} and end ${sentence_end}`);
        let sentence = ""
        for (let i = sentence_start; i <= sentence_end; i++) {
            sentence = sentence.concat(this.state.data[i].input);
            if (i != sentence_end) {
                sentence = sentence.concat(" ");
            }
        }
        let sentence_to_modify = {sentence:sentence, sentence_id: sentence_id, annotation_id: null};
        if ('annotation_id' in this.state.data[sentence_start]) {
            sentence_to_modify.annotation_id = this.state.data[sentence_start].annotation_id;
        }

        this.setState({
            sentence_to_modify: sentence_to_modify,
            modify_sentence: true,
        });
    }

    async resubmitSentence(new_sentence) {
        // TODO make different requests depending on the eaf file or text
        this.setState({
            modify_sentence: false,
        });

        const inputText = new_sentence;
        const data = {
            text: inputText, 
            model: 'fairseq',
            nbest: this.state.data[0].nbest, 
            getSeg: this.state.hasSeg,
            getGloss: this.state.hasGloss
        };

        console.log(data);

        console.log(this.state.data);
        //  submit a new job and get a new job id (Changed: requesting batch job)
        const request = await requestData('/api/job/batch', data, 'POST');
        // wait for the job to finish and get the new data
        let status = {status:false};

        while(!status.status) {
            status = await requestData(`/api/job/${request.job_id}/batch`);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        const modified_sentence = await requestData(`/api/job/${request.job_id}/batch/download`);

        // exchange the tokens in data
        const sentence_id = this.state.sentence_to_modify.sentence_id;
        const sentence_boundary = this.determineSentenceBoundaries(sentence_id);
        const start = sentence_boundary[0];
        const end = sentence_boundary[1];
        // console.log(`start is ${start}, end is ${end}, modified sentence ${modified_sentence}`);

        // isolate the part before the modified sentence if it exists
        // then isolate the part after the modified sentence if it exists
        // then stich the before part with modified sentence and the after part.
        const before_modified = this.state.data.slice(0, start);
        let sentence_id_current = sentence_id;

        // modify sentence id's after modification in case if the modified sentence has been split into 2 or more sentences

        let updated_data = before_modified;


        console.log(`the annotation id of sentence to modify is ${this.state.sentence_to_modify.annotation_id}`)
        if (modified_sentence.length > 0) {
            console.log("i am inside the conditional")
            if (this.state.sentence_to_modify.annotation_id === null) {
                console.log("the annotation id is null")
                // if the iniput type originally was text, then recalculate sentence id, 
                // as a sentence can be split during resubmitting a sentence.
                let sentence_id_in_modified = modified_sentence[0].sentence_id;
                modified_sentence[0].sentence_id = sentence_id_current;
    
                for (let i = 1; i < modified_sentence.length; i++) {
                    if (modified_sentence[i].sentence_id != sentence_id_in_modified) {
                        sentence_id_current++;
                    }
                    sentence_id_in_modified = modified_sentence[i].sentence_id;
                    modified_sentence[i].sentence_id = sentence_id_current;
                    console.log(`${sentence_id_current} is current id and modified sentence has id ${modified_sentence[i].sentence_id}`);
                }
            } else {
                console.log("I am inside else")
                // if the input type origianlly was an eaf file, then simply assign the same sentence id 
                // and annotation id to the entire resubmitted output as originally, as we do not allow
                // changing annotation id for the resubmitted chunk.
                const original_sentence_id = this.state.sentence_to_modify.sentence_id;
                const original_annotation_id = this.state.sentence_to_modify.annotation_id;
                console.log(`original annotation id is ${original_annotation_id}`)
                console.log(`original sentence id ${original_sentence_id}`)
                console.log(original_sentence_id);
                for (let i = 0; i < modified_sentence.length; i++) {
                    modified_sentence[i].sentence_id = original_sentence_id;
                    modified_sentence[i].annotation_id = original_annotation_id;
                }
            }


            updated_data = updated_data.concat(modified_sentence);
        }

        sentence_id_current++;

        console.log(`the length of data is ${this.state.data.length} and the end is on ${end}`);
        if (end + 1 !== this.state.data.length) {
            const after_modified = this.state.data.slice(end + 1, this.state.data.length);

            let previous_id = after_modified[0].sentence_id;
            after_modified[0].sentence_id = sentence_id_current;

            for (let i = 1; i < after_modified.length; i++) {
                if (after_modified[i].sentence_id != previous_id) {
                    sentence_id_current++;
                }
                previous_id = after_modified[i].sentence_id;
                after_modified[i].sentence_id = sentence_id_current;
            }
            updated_data = updated_data.concat(after_modified);
        }
    
        // console.log(`new data length is ${updated_data.length}`)
        // for (let i=0; i< updated_data.length; i++) {
        //     console.log(updated_data[i].annotation_id);
        // }

        
        // update the state

        // need to update the state in such a way so that the results table
        // shows at the panel with the updated sentence

        const {pages, sentence_boundaries} = this.computePages(updated_data);
        // make a dictionary {key: list of indixes} and store it in state
        // but also make it updatable?
        const token_dictionary = this.makeTokenDictionary(updated_data);

        
        // determine the lower and upper bounds of the page on which the modified setences appears
        let lower_bound;
        let upper_bound;

        for (let k = 0; k < pages.length; k++) {
            if (sentence_id in pages[k].sentences_included) {
                lower_bound = pages[k].first_token;
                upper_bound = pages[k].last_sentence_end;
                break;
            }
        }

        this.setState({
            lower_bound: lower_bound,
            upper_bound: upper_bound,
            pages: pages,
            data: updated_data,
            token_dictionary: token_dictionary,
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_boundaries,
        });
    }

    async handleSave(filename, format, saveGloss, saveSeg) {
        console.log(this.state.data);

        // if the format is text, save a file of preferred segmentations. If it's an EAF, convert and then save
        if (format === 'txt') {
            // generate a string representing the preferred segmentations of all the tokens. Sentences separated by lines.
            let seg_tokens = [];
            let gloss_tokens = [];
            let curr_sentence = -1;

            for (let i=0; i < this.state.data.length; i++) {
                let curr_token = this.state.data[i];

                if (curr_token['sentence_id'] > curr_sentence) {
                    seg_tokens.push([]);
                    gloss_tokens.push([]);
                    curr_sentence++;
                }

                seg_tokens[seg_tokens.length - 1].push(curr_token['preferred_segmentation']);
                gloss_tokens[gloss_tokens.length - 1].push(curr_token['preferred_gloss']);
            }

            // construct a string from the two list of lists, depending on preferences
            let output_string = '';
            for (let i=0; i<seg_tokens.length; i++) { 
                if (saveSeg) {
                    output_string += seg_tokens[i].join(' ') + '\n';
                }
                if (saveGloss) {
                    output_string += gloss_tokens[i].join(' ') + '\n';
                }
                if (saveSeg && saveGloss && i < seg_tokens.length - 1) {
                    output_string += '\n';
                }
            }
            // let output_string = '';
            // for (const sent of output_tokens) {
            //     output_string += sent.join(' ') + '\n';
            // }

            console.log(output_string);

            // download text as a blob
            let output_blob = new Blob([output_string], {type: "text/plain;charset=utf-8"});
            var link = document.createElement('a');
            link.download = filename + '.' + format;
            link.href = window.URL.createObjectURL(output_blob);
            link.click();
        } else {
            let model_type = 'both';
            if (!saveGloss) {
                model_type = 'segmentation';
            } else if (!saveSeg) {
                model_type = 'gloss';
            }

            const data = {id: this.props.jobId, tokens: this.state.data, models: model_type};
            console.log(data);

            // submit an API request
            const result = await requestData('/api/job/convert', data, 'POST');
            console.log(result);

            // wait for the job to finish and get the new data
            let status = {status:false};

            while(!status.status) {
                status = await requestData(`/api/job/${this.props.jobId}/get_eaf_file`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            console.log(status);
            let save_text = status.written_elan;

            // download text as a blob
            let output_blob = new Blob([save_text], {type: "text/plain;charset=utf-8"});
            var link = document.createElement('a');
            link.download = filename + '.' + format;
            link.href = window.URL.createObjectURL(output_blob);
            link.click();
        }
        
    }

    render() {
        return (
            <div>
                {this.state.modify_sentence && (<ResubmitSentenceSection 
                        sentence={this.state.sentence_to_modify.sentence}
                        onSubmit={(new_sentence) => {this.resubmitSentence(new_sentence)}}
                        cancelSentenceResubmission={this.cancelSentenceResubmission}
                    />)}
                <div id="completed_message">
                    <SideMenu 
                        data={this.state.pages}
                        hasSeg={this.state.hasSeg}
                        hasGloss={this.state.hasGloss}
                        currPage={this.state.currPage}
                        onClick={(lower_b, upper_b, i) => this.handleClick(lower_b, upper_b, i)}
                        onRetrieveSentence={(sentence_id) => {this.retrieveSentenceToModify(sentence_id)}}
                        handleSave={(filename, format, saveGloss, saveSeg) => this.handleSave(filename, format, saveGloss, saveSeg)}
                    />
                    <DynamicResultsTable 
                        data={this.state.data} 
                        lower_bound={this.state.lower_bound} 
                        upper_bound={this.state.upper_bound}
                        hasSeg={this.state.hasSeg}
                        hasGloss={this.state.hasGloss}
                        updatePreferredSegmentation = {
                            (index, modelType, newPreferred, isCustom, update_mode) => 
                                this.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                        }
                    />
                </div>
                <div id="completed_message">
                    <PageNav 
                        data={this.state.pages}
                        currPage={this.state.currPage}
                        onClick={(lower_b, upper_b, i) => this.handleClick(lower_b, upper_b, i)}
                    /> 
                </div>    
            </div>
        )
    }
}

// TODO fix bug in sentence resubmission

// add sentence indexing
// page table - show number of sentences that fit into 100 tokens
// and do not cut sentence in the middle
// below page add buttons for sentences
// when you hove over these buttons, the sentence cells will
// will highlight.
// when you click on sentence edit button, a window with input sentence will show up
// above the results table with "resubmit" button
// the whole table will then refresh
// how should i hold the data in a JSON object then?
// as token id, you can use sentence id and index within a sentence

