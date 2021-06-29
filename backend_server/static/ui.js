'use strict';

class Cell extends React.Component {
    constructor(props){
        super(props);

        const dropdown_list = this.initilizeList();

        this.state = {
          location: dropdown_list
        }
    }

    initilizeList() {
        // console.log(`this: ${this} props: `, this.props);
        const segmentation_list = this.props.token["segmentation"];
        let dropdown_list = [];
        for (let i = 0; i < segmentation_list.length; i++) {
            const option = {
                id: i,
                title: segmentation_list[i],
                selected: false,
                key: 'location'
            };
            dropdown_list.push(option);
        }

        const option = {
            id: segmentation_list.length,
            title: "Custom",
            selected: false,
            key: 'location'
        };
        dropdown_list.push(option);

        return dropdown_list;
    }

    changeList(newPreferred, isCustom, update_mode) {
        this.props.updatePreferredSegmentation(this.props.index, newPreferred, isCustom, update_mode);
        this.setState({
            location: this.initilizeList(),
        });
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
        return (
            <div className="cell">
                <p>{this.props.token["input"]}</p>
                <p>{this.props.token["preferred_segmentation"]}</p>
                <Dropdown  
                    title={this.props.token["segmentation"][0]}
                    list={this.state.location}
                    resetThenSet={this.resetThenSet}
                    changeList = {(newPreferred, isCustom, mode) => this.changeList(newPreferred, isCustom, mode)}
                />
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

    selectItem = (item) => {
        const { resetThenSet } = this.props;
        const { title, id, key } = item;
      
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

    handleRadioChange(event) {
        let update_mode = "all";
        if (event.target.value == "only_this") {
            update_mode = "only_this";
            alert("Only this option is chosen");
        } else if (event.target.value == "all_before") {
            update_mode = "all_before";
            alert("All before option is chosen");
        } else {
            alert("All option is chosen");
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
                                id="all_before" 
                                name="update_mode" 
                                value="all" 
                                checked={this.state.selected_update_mode === "all_before"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all_before" className="mode_button">all</label>
                        <input  type="radio" 
                                id="all" 
                                name="update_mode" 
                                value="all"
                                checked={this.state.selected_update_mode === "all"}
                                onChange={this.handleRadioChange}
                        />
                        <label htmlFor="all" className="mode_button">all</label>
                    </div>
                    <input type="submit"></input>
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
        const column_number = (tokens_included >= 10) ? 10 : tokens_included;
        const row_number = Math.ceil(tokens_included/10);

        let current_index = 0;
        // the outer loop will count up to ten, and break if there is less
        for (let i = 0; i < row_number; i++) {
            let row = [];
            for (let j = 0; j < column_number; j++) {
                const current_token = current_index + this.props.lower_bound;
                if (current_token > this.props.upper_bound) {
                    break;
                }
                console.log(`Lower bound is ${this.props.lower_bound} and current_index is ${current_index} and index is ${current_index + this.props.lower_bound}`)
                row.push(
                    <td key={j}>
                        <Cell 
                            token={this.props.data[current_token]}
                            index={current_index + this.props.lower_bound}
                            updatePreferredSegmentation = {
                                ( index, newPreferred, isCustom, update_mode) => 
                                this.props.updatePreferredSegmentation(index, newPreferred, isCustom, update_mode)
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

class Legend extends React.Component {
    render() {
        return (
            <div id="legend">
                <h3>Table Legend</h3>
                <p className="input_token">Input token</p>
                <p> Preferred segmentation</p>
                <p id="segmentation_list_legend">
                    List of n-best segmentations
                </p>
            </div>
        )
    }
}

class PageTableCellButton extends React.Component {
    handleClick() {

    }

    render() {
        return (
            <button 
                className="range_button"
                onClick={() => this.props.onClick(this.props.lower_bound, this.props.upper_bound, this.props.page_index)}
            >
                {this.props.lower_bound} - {this.props.upper_bound}
            </button>
        )
    }
}

class PageTableSentenceButton extends React.Component {
    render() {
        return (
            <button 
                className="sentence_button"
                onClick={() => {this.props.onClick(this.props.sentence_id)}}
                className="range_button"
            >
                Modify sentence {this.props.sentence_id}
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

        this.state = {
            sentences_included: this.props.data[0][2],
        };
    }

    onClick(lower_b, upper_b, i) {
        this.setState({
            sentences_included: this.props.data[i][2],
        });
        this.props.onClick(lower_b, upper_b);
    }



    render() {
        const rows_data = this.props.data;
        let rows = [];
        for (let i = 0; i < rows_data.length; i++) {
            rows.push(
                <tr key={i}>
                    <td>
                        <PageTableCellButton 
                            lower_bound={rows_data[i][0]} 
                            upper_bound={rows_data[i][1]}
                            page_index = {i}
                            onClick={(lower_b, upper_b, i) => this.onClick(lower_b, upper_b, i)}
                        />
                    </td>
                </tr>
            );
        }

        let sentence_rows = [];
        for (let j = 0; j < this.state.sentences_included.length; j++) {
            sentence_rows.push(
                <tr key={j}>
                    <td>
                        <PageTableSentenceButton 
                            sentence_id={this.state.sentences_included[j]}
                            onClick={(sentence_id) => {this.props.onRetrieveSentence(sentence_id)}}
                        />
                    </td>
                </tr>
            );
        }

        return (
            <div id="range_table_wrapper">
             <table>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p>Sentences in this window:</p>
            <table>
                <tbody>
                    {sentence_rows}
                </tbody>
            </table>
            </div>
        )
    }
}



class SideMenu extends React.Component {
    render() {
        return (
            <div className="range_and_save">
                <Legend />
                <PageTable 
                    data={this.props.data}
                    onClick={(lower_b, upper_b) => this.props.onClick(lower_b, upper_b)}
                    onRetrieveSentence={(sentence_id) => {this.props.onRetrieveSentence(sentence_id)}}
                />
                <button id="save_changes_button" className="job_buttons">
                    Save changes
                </button>
            </div>

        );
    }
};

class ResubmitSentenceSection extends React.Component {
    // TODO add controlled component
    constructor(props){
        super(props)
        this.state = {
          value: this.props.sentence,
        //   set update_mode to default checked radio button value
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
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
            </form>
        );

    }
}

class ResultsSection extends React.Component {
    constructor(props) {
        super(props);
        let rows = [];
        const token_list = [...props.data];
        const token_number = token_list.length;

        let first_token = 0;
        let last_sentence_end = 0;
        let current_sentence_id = token_list[0].sentence_id;

        let sentence_start = {}
        sentence_start[token_list[0].sentence_id] = 0;

        const max_tokens_per_view = 50;
        for (let i = 0; i < token_number; i++) {
            // when you exceed max tokens, make a row
            if (current_sentence_id != token_list[i].sentence_id) {
                last_sentence_end = i - 1;
                current_sentence_id = token_list[i]["sentence_id"];
                sentence_start[current_sentence_id] = i;
            }

            if (i == token_number - 1) {
                last_sentence_end = i;
            }

            if (i - first_token + 1 >= max_tokens_per_view || i == token_number - 1) {
                last_sentence_end = first_token >= last_sentence_end ? i : last_sentence_end;
                // console.log(sentence_start);
                // console.log(`Start: ${first_token} and end ${last_sentence_end}`);
                let sentences_included = [];
                sentences_included.push(token_list[first_token].sentence_id);
                // console.log(sentences_included);
                for (let key in sentence_start) {
                    if (sentence_start[key] > first_token && sentence_start[key] <= last_sentence_end) {
                        sentences_included.push(key);
                    }           
                }
                rows.push([first_token, last_sentence_end, sentences_included]);
                first_token = last_sentence_end + 1;
            }
        }
        
        this.state = {
            lower_bound: rows[0][0],
            upper_bound: rows[0][1],
            rows: rows,
            // below is a copy of input data
            data: [...props.data],
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_start,
        };
    }

    handleClick(lower_b, upper_b) {
        this.setState({
            lower_bound: lower_b,
            upper_bound: upper_b,
        });
    }

    updatePreferredSegmentation(index, newPreferred, isCustom, update_mode) {
        // TODO do something with the update mode
        const newData = [...this.state.data];
        console.log(`The index is ${index}`);
        newData[index]["preferred_segmentation"] = newPreferred;

        if (isCustom === true) {
            newData[index]["segmentation"].push(newPreferred);
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
        this.setState({
            sentence_to_modify: {sentence:sentence, id: sentence_id},
            modify_sentence: true,
        });
    }

    async resubmitSentence(new_sentence) {
        // TODO implement handler
        const inputText = new_sentence;
        // TODO expand on that if other models are here
        const isColing = this.state.data[0].model === "coling";
        let data;
        if (isColing) {
            data = {text:inputText, model:'coling'};
        } else {
            data = {text:inputText, model:'fairseq'};
        }
        //  submit a new job and get a new job id
        const request = await requestData('/api/job', data, 'POST');

        let status = {status:false};

        while(!status.status) {
            status = await requestData(`/api/job/${request.job_id}`);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        const modified_sentence = await requestData(`/api/job/${request.job_id}/download`);

        // exchange the tokens in data
        const sentence_id = this.state.sentence_to_modify.id;
        const sentence_boundary = this.determineSentenceBoundaries(sentence_id);
        const start = sentence_boundary[0];
        const end = sentence_boundary[1];
        // console.log(`start is ${start}, end is ${end}, modified sentence ${modified_sentence}`);

        const before_modified = this.state.data.slice(0, start);
        
        let updated_data = before_modified.concat(modified_sentence);

        if (end != this.state.data.length) {
            const after_modified = this.state.data.slice(end + 1, this.state.data.length);
            updated_data = updated_data.concat(after_modified);
        }
    
        console.log(`new data length is ${updated_data.length}`)

        // update the state

        // need to update the state in such a way so that the results table
        // shows at the panel with the updated sentence

        let rows = [];
        const token_list = updated_data;
        const token_number = token_list.length;

        let first_token = 0;
        let last_sentence_end = 0;
        let current_sentence_id = token_list[0].sentence_id;

        let sentence_start = {}
        sentence_start[token_list[0].sentence_id] = 0;

        const max_tokens_per_view = 50;
        for (let i = 0; i < token_number; i++) {
            // when you exceed max tokens, make a row
            if (current_sentence_id != token_list[i].sentence_id) {
                last_sentence_end = i - 1;
                current_sentence_id = token_list[i]["sentence_id"];
                sentence_start[current_sentence_id] = i;
            }

            if (i == token_number - 1) {
                last_sentence_end = i;
            }

            if (i - first_token + 1 >= max_tokens_per_view || i == token_number - 1) {
                last_sentence_end = first_token >= last_sentence_end ? i : last_sentence_end;
                // console.log(sentence_start);
                // console.log(`Start: ${first_token} and end ${last_sentence_end}`);
                let sentences_included = [];
                sentences_included.push(token_list[first_token].sentence_id);
                // console.log(sentences_included);
                for (let key in sentence_start) {
                    if (sentence_start[key] > first_token && sentence_start[key] <= last_sentence_end) {
                        sentences_included.push(key);
                    }           
                }
                rows.push([first_token, last_sentence_end, sentences_included]);
                first_token = last_sentence_end + 1;
            }
        }
        
        let lower_bound;
        let upper_bound;

        for (let k = 0; k < rows.length; k++) {
            if (sentence_id in rows[k][2]) {
                lower_bound = rows[k][0];
                upper_bound = rows[k][1];
            }
        }

        this.setState({
            lower_bound: lower_bound,
            upper_bound: upper_bound,
            rows: rows,
            data: updated_data,
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_start,
        });

        // TODO make it more efficient so that you do not have to traverse the entire
        // data again
    }

    render() {
        return (
            <div>
                {this.state.modify_sentence && (<ResubmitSentenceSection 
                        sentence={this.state.sentence_to_modify.sentence}
                        onSubmit={(new_sentence) => {this.resubmitSentence(new_sentence)}}
                    />)}
                <div id="completed_message">
                    <SideMenu 
                        data={this.state.rows} 
                        onClick={(lower_b, upper_b) => this.handleClick(lower_b, upper_b)}
                        onRetrieveSentence={(sentence_id) => {this.retrieveSentenceToModify(sentence_id)}}
                    />
                    <ResultsTable 
                        data={this.state.data} 
                        lower_bound={this.state.lower_bound} 
                        upper_bound={this.state.upper_bound}
                        updatePreferredSegmentation = {
                            (index, newPreferred, isCustom, update_mode) => 
                                this.updatePreferredSegmentation(index, newPreferred, isCustom, update_mode)
                        }
                    />
                </div>
            </div>
        )
    }
}

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

