import React, { useState, useEffect } from 'react';
import Switch from 'rc-switch';
import 'rc-switch/assets/index.css';
import { Tooltip } from 'reactstrap';
import { getCurrentColor, setCurrentColor } from '../../helpers/Utils';

const TopnavDarkSwitch = () => {
  const [switchChecked, setSwitchChecked] = useState(false);
  const [tooltipOpen, setTooltipOpen] = useState(false);

  

  const changeMode = () => {
    const style = document.createElement("style");
    if (!switchChecked){
      style.textContent = "img{opacity: 0.1}"
      style.id = "hideImages";
      document.head.append(style);
      setSwitchChecked(!switchChecked);

    }else{
      document.getElementById("hideImages").remove();
      setSwitchChecked(!switchChecked);
    }
  }

  return (
    <div className="d-none d-md-inline-block align-middle mr-3">
      <Switch
        id="tooltip_switch"
        className="custom-switch custom-switch-primary custom-switch-small"
        checked={switchChecked}
        onChange={changeMode}
      />
      <Tooltip
        placement="left"
        isOpen={tooltipOpen}
        target="tooltip_switch"
        toggle={() => setTooltipOpen(!tooltipOpen)}
      >
        Hide Images
      </Tooltip>
    </div>
  );
};
export default TopnavDarkSwitch;
