import './App.css';
import Graph from "react-graph-vis";
import React, { useState } from "react";
import ApiUtil from './Utils/ApiUtil';
import HttpUtil from './Utils/HttpUtil';
//import './network.css'

function App() {

  const [structureState, setStructureState] = useState(
    [] // 文字版
  );

  const [graphState, setGraphState] = useState(
    {
      nodes: [],
      edges: []
    }
  );

  const options = {
    layout: {
      hierarchical: false
    },
    edges: {
      color: "#34495e"
    }
  };

  const clearState = () => {
    setStructureState([]);
    setGraphState({
      nodes: [],
      edges: []
    })
  };

  const updateStructure = (update) => {
    var current_structure = JSON.parse(JSON.stringify(structureState));
    if (update.length === 0) {
      console.log("0 output")
      return;
    }

    // 清空当前状态
    setStructureState([]);

    // 根据任务类型创建不同的表格
    const renderTable = (data) => {
      if (taskState.taskValue === 'RE') {
        return (
          <table className="result-table RE">
            <thead>
              <tr>
                <th>元素名称</th>
                <th>元素值</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => {
                const parsed = JSON.parse(item);
                return (
                  <>
                    <tr key={`${index}-entity1`}>
                      <td>实体1</td>
                      <td>{parsed[0]}</td>
                    </tr>
                    <tr key={`${index}-relation`}>
                      <td>关系</td>
                      <td>{parsed[1]}</td>
                    </tr>
                    <tr key={`${index}-entity2`}>
                      <td>实体2</td>
                      <td>{parsed[2]}</td>
                    </tr>
                  </>
                );
              })}
            </tbody>
          </table>
        );
      } else if (taskState.taskValue === 'NER') {
        return (
          <table className="result-table NER">
            <thead>
              <tr>
                <th>元素名称</th>
                <th>元素值</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => {
                const parsed = JSON.parse(item);
                return (
                  <>
                    <tr key={`${index}-entity`}>
                      <td>实体</td>
                      <td>{parsed[0]}</td>
                    </tr>
                    <tr key={`${index}-type`}>
                      <td>类型</td>
                      <td>{parsed[1]}</td>
                    </tr>
                  </>
                );
              })}
            </tbody>
          </table>
        );
      } else if (taskState.taskValue === 'EE') {
        return (
          <table className="result-table EE">
            <thead>
              <tr>
                <th>元素名称</th>
                <th>元素值</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => {
                const parsed = JSON.parse(item);
                return Object.entries(parsed).map(([eventType, args], eventIndex) => (
                  <>
                    <tr key={`${index}-${eventIndex}-type`}>
                      <td>事件类型</td>
                      <td>{eventType}</td>
                    </tr>
                    {Object.entries(args)
                      .filter(([role]) => role !== 'trigger')
                      .map(([role, value], argIndex) => (
                        <tr key={`${index}-${eventIndex}-${argIndex}`}>
                          <td>{role}</td>
                          <td>{value}</td>
                        </tr>
                      ))}
                  </>
                ));
              })}
            </tbody>
          </table>
        );
      }
    };

    // 更新状态
    setStructureState(update);
    
    // 渲染表格
    const tableElement = renderTable(update);
    setStructureState([tableElement]);
  }

  const getColorS = () => {
    var Arr = ["#FF5733", "#C70039", "#ffc4de", "#ecb9b9", "#DAF7A6", "#f7efa6"];  
    var n = Math.floor(Math.random() * Arr.length + 1)-1;
    return Arr[n];
  }

  const getColorO = () => {
    var Arr = ["#D5F5E3", "#AED6F1", "#FDEBD0", "#E5E7E9", "#F2D7D5", "#D6EAF8"]; 
    var n = Math.floor(Math.random() * Arr.length + 1)-1;
    return Arr[n];
  }

  const updateGraph = (updates, task) => {
    // updates will be provided as a list of lists
    // each list will be of the form [ENTITY1, RELATION, ENTITY2] or [ENTITY1, COLOR]

    var current_graph = JSON.parse(JSON.stringify(graphState));

    if (updates.length === 0) {
      return;
    }

    // check type of first element in updates
    if (typeof updates[0] === "string") {
      // updates is a list of strings
      updates = [updates]
    }

    if (task === "RE"){
      updates.forEach(update => {
        if (update.length === 3) {
          // update the current graph with a new relation
          const [entity1, relation, entity2] = update;
  
          // check if the nodes already exist
          var node1 = current_graph.nodes.find(node => node.id === entity1);
          var node2 = current_graph.nodes.find(node => node.id === entity2);
  
          if (node1 === undefined) {
            current_graph.nodes.push({ id: entity1, label: entity1, color: getColorS() });
          }
  
          if (node2 === undefined) {
            current_graph.nodes.push({ id: entity2, label: entity2, color: getColorO() });
          }
  
          // check if an edge between the two nodes already exists and if so, update the label
          // 图不支持一对结点多个边。
          var edge = current_graph.edges.find(edge => edge.from === entity1 && edge.to === entity2);
          if (edge !== undefined) {
            edge.label = relation;
            return;
          }
  
          current_graph.edges.push({ from: entity1, to: entity2, label: relation });
  
        }
      });
    } else if (task === "NER"){
      updates.forEach(update => {
        if (update.length === 2) {
          // update the current graph with a new relation
          const [entity, etype] = update;

          const enet = etype+": "+entity;
  
          // check if the nodes already exist
          var node1 = current_graph.nodes.find(node => node.id === enet);
  
          if (node1 === undefined) {
            current_graph.nodes.push({ id: enet, label: enet, color: getColorS()});
          }
  
        }
      });
    }else if (task === "EE"){
      updates.forEach( update => {
        Object.keys(update).forEach(key1 => {
        
          // check if the nodes already exist
          var node1 = current_graph.nodes.find(node => node.id === key1);
  
          if (node1 === undefined) {
            current_graph.nodes.push({ id: key1, label: key1, color: getColorS() });
          }

          const update2 = update[key1];

          Object.keys(update2).forEach(key2 => {
            const value2 = update2[key2];
            // check if the nodes already exist
            var node1 = current_graph.nodes.find(node => node.id === value2);
    
            if (node1 === undefined) {
              current_graph.nodes.push({ id: value2, label: value2, color: getColorO() });
            }
            
            // check if an edge between the two nodes already exists and if so, update the label
            // 图不支持一对结点多个边。
            var edge = current_graph.edges.find(edge => edge.from === key1 && edge.to === value2);
            if (edge !== undefined) {
              edge.label = key2;
              return;
            }
    
            current_graph.edges.push({ from: key1, to: value2, label: key2 });
          });  
        });

      });
    }
    
    //console.log(current_graph);
    setGraphState(current_graph);
  };



  const queryPrompt = (f2b) => {
    console.log(f2b);
    HttpUtil.post(ApiUtil.API_STAFF_UPDATE, JSON.stringify(f2b)).then(
      re => {
        console.log(re);
        var update = re['result'];
        console.log(update);
        console.log(update[0]);
        // 图版
        if (typeof update[0] !== "string") { //后端如果没结果或者错误的字符串
          updateGraph(update, re['task']);
        }
        // 文字版输出
        var str_update = [];
        update.forEach(ut => {
          str_update.push(JSON.stringify(ut));
        });
        console.log(str_update);
        console.log(str_update[0]);
        updateStructure(str_update);

        document.body.style.cursor = 'default';
        document.getElementsByClassName("generateButton")[0].disabled = false;
      }
    ).catch((error) => {
      console.log(error);
      alert(error);
      document.body.style.cursor = 'default';
      document.getElementsByClassName("generateButton")[0].disabled = false; //出错则释放，为了能再次使用
    }); 
    
  }


  const createIE = () => {
    document.body.style.cursor = 'wait';
    document.getElementsByClassName("generateButton")[0].disabled = true;

    const prompt = document.getElementsByClassName("searchBar")[0].value;
    const prompt1 = document.getElementById("prompt1").value;
    // var access = document.getElementsByClassName("apiKeyTextField")[0].value;
    //console.log(apiKey);
    if (prompt.length === 0){
      alert('empty sentence');
      document.body.style.cursor = 'default';
      document.getElementsByClassName("generateButton")[0].disabled = false;
      return
    }

    var f2b = {
      "sentence": prompt,
      "type": prompt1,
      // "access": access,
      "task": taskState.taskValue,
      "lang": lanState.lanValue,
    }
        

    queryPrompt(f2b);
  }

  const lists = structureState.map((item, index) => (
    <div key={index}>{item}</div>
  ));

  // 语言选项
  const [lanState, setLanState] = useState(
    {lanValue: "english"}
  );

  const handleChange = (event) => {
    console.log(event);
    console.log(event.target.value);
    //setLanState({lanValue: event.target.value}, 
    //  () => {console.log(lanState)});
    setLanState({lanValue: event.target.value}); // 坑：set状态后，lanState值不会立即改变，因为react是渲染周期结束后才更新值。
  };

  // 任务选项
  const [taskState, setTaskState] = useState({
    taskValue: 'EE'  // 固定为 EE
  });

  // <form>能控制radio为一组。
  return (
    <div className='container'>
      <h1 className="headerText">事件抽取演示系统 </h1>
      <center>
        <div className='inputContainer'>
          <input className="searchBar" placeholder="Input sentence..."></input>
          <input className="typeList" id="prompt1" placeholder="Optional, type list"></input>
          <button className="generateButton" onClick={createIE}>Generate</button>
          <button className="clearButton" onClick={clearState}>Clear</button>
        </div>
      </center>
      <div className='resultContainer'>
        <div className='graphContainer'>
          <Graph graph={graphState} options={options} style={{ height: "640px" }} />
        </div>
        <div className='tableContainer'>
          {lists}
        </div>
      </div>
    </div>
  );
}

export default App;
