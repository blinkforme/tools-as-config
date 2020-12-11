

package conf
{
    import manager.ConfigManager;

	public class cfg_vip
	{
        public static function init(sheet:Object):cfg_vip
        {
            var a:cfg_vip = new cfg_vip();

            
            a.register_vip_extra_reward_nums=sheet[1];
            
            a.reward_item_price2=sheet[2];
            
            a.reward_item_price1=sheet[3];
            
            a.is_send_gift=sheet[18];
            
            a.register_vip_extra_reward_ids=sheet[4];
            
            a.reset_basic_coin=sheet[15];
            
            a.reward_item_price1_title=sheet[16];
            
            a.real_hitup_rate=sheet[6];
            
            a.right_title=sheet[7];
            
            a.right_content=sheet[8];
            
            a.vip_package=sheet[9];
            
            a.vip=sheet[10];
            
            a.base_coin_values=sheet[17];
            
            a.contest_score_vip_rate=sheet[11];
            
            a.exp=sheet[12];
            
            a.base_coin_times=sheet[13];
            
            a.vip_reward_image=sheet[0];
            
            a.id=sheet[14];
            
            a.change=sheet[5];
            
            a.hide_txt=sheet[19];
            

			return a;
        }
        public static function instance(key:Object):cfg_vip
		{
            return ConfigManager.getConfObject("cfg_vip",key) as cfg_vip;
		}


        
        public var register_vip_extra_reward_nums:Array;
        
        public var reward_item_price2:int;
        
        public var reward_item_price1:int;
        
        public var is_send_gift:int;
        
        public var register_vip_extra_reward_ids:Array;
        
        public var reset_basic_coin:int;
        
        public var reward_item_price1_title:String;
        
        public var real_hitup_rate:Number;
        
        public var right_title:String;
        
        public var right_content:Array;
        
        public var vip_package:Array;
        
        public var vip:int;
        
        public var base_coin_values:int;
        
        public var contest_score_vip_rate:Number;
        
        public var exp:int;
        
        public var base_coin_times:int;
        
        public var vip_reward_image:String;
        
        public var id:int;
        
        public var change:Array;
        
        public var hide_txt:String;
        






	}
}