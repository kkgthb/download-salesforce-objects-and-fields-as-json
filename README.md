
## TL;DR for experienced devs

```
cci task run get_schema_details --org your-clever-alias
```

Dumps Task, Lead, and Contact definitions to `output/schema.json` if you edit nothing before running.  [See example output.](https://github.com/kkgthb/download-salesforce-objects-and-fields-as-json/blob/main/example-output.json)

---

## Prereqs

### Install CumulusCI

Install the [CumulusCI command-line tool](https://cumulusci.readthedocs.io/en/stable/get-started.html#install-cumulusci) onto your computer.

_(I don't think you also need the [SFDX](https://developer.salesforce.com/tools/sfdxcli) command-line tool, a.k.a. "Salesforce CLI," installed onto your computer, but if these instructions don't work, see if that helps and let me know.)_

### Download this codebase

Download a copy of this codebase into a folder on your computer's hard drive.

### File edits

In the copy of this codebase that you just downloaded, open the file `cumulusci.yml`.

Edit the list `tasks.get_schema_details.options.objects` list within it to add/remove objects that you'd like to dump details from into a JSON format on your hard drive.

Or just comment out _(or delete)_ the `objects` property altogether to dump all objects in the entire Salesforce org to disk.

_(Note:  Either way, you're downloading everything.  The `objects` property just controls how big of a file you dump to disk.)_

### Log the folder into an org with CCI

From a command-line prompt in your computer that's **running within** the context of **the folder** you downloaded this project to...

Run the following to see if you already logged this project into Salesforce with CumulusCI earlier and just forgot:

```sh
cci org list
```

Ignore the table of **scratch orgs** with names like `beta`, `dev`, etc.  You're looking to see if there's anything in the table of **connected orgs** below it.

If you find what you're looking for, you can skip the rest of this section, substituting the value you found in the **Name** column for `your-clever-alias` in the rest of my instructions.

Otherwise, pick something to use as an "alias" for the org within the context of running code from the folder that you've downloaded this CumulusCI project into.  I'll use the phrase `your-clever-alias` in code snippets, but you can probably do a better job than that.

From a command-line prompt in your computer that's **running within** the context of **the folder** you downloaded this project to, run one of the following commands:

1. For a production org or [dev org](https://developer.salesforce.com/signup){:target="_blank"} that _doesn't_ have a custom domain, you'll do:
    ```sh
    cci org connect your-clever-alias --global-org --login-url https://login.salesforce.com/
    ```
1. For a production org or [dev org](https://developer.salesforce.com/signup){:target="_blank"} that that _does_ have a custom domain, you'll do:
    ```sh
    cci org connect your-clever-alias --global-org --login-url https://your-custom-domain.my.salesforce.com/
    ```
1. For a sandbox that _doesn't_ have a custom domain, you'll do:
    ```sh
    cci org connect your-clever-alias --global-org --sandbox --login-url https://customdomain.my.salesforce.com/
    ```
1. For a sandbox that _does_ have a custom domain, you'll do:
    ```sh
    cci org connect your-clever-alias --global-org --sandbox --login-url https://your-custom-domain--the-sandbox-name.sandbox.my.salesforce.com/
    ```
1. For a scratch org called `beta` that already exists but that you spun up in the context of a totally different project called `Other-Project` _(look at its `cumulusci.yml` file's `project.name` property)_, you'll do:
    ```sh
    cci org import Other-Project__beta your-clever-alias
    ```

When your web browser opens to a Salesforce login page, log into that org as yourself.  If prompted, go ahead and say you'll allow CumulusCI to do things as you.  When you're all done, you should see some sort of `http://localhost`-based URL in your browser saying something like, "Congratulations! Your authentication succeeded."  You can close that browser tab now.

You should now see `your-clever-alias` in the **Name** column of an entry in the table under **connected orgs** when you run the `cci org list` command.  _(Or, if you imported another project's running scratch org, it might be up under **scratch orgs**)_.

If you forget to log CumulusCI into the org you'd like to download from and give it an alias of `your-clever-alias`, your attempt to download data from `your-clever-alias` through `cci task run get_schema_details --org your-clever-alias` is going to fail with the following error message:

> Error: Org with name 'your-clever-alias' does not exist.

---

## Run the downloader

From a command-line prompt in your computer that's **running within** the context of **the folder** you downloaded this project to, run the following command:

```sh
cci task run get_schema_details --org your-clever-alias
```

When the process stops running, you should have a file called `schema.json` in a sub-folder of the folder you downloaded this project to called `output`.

Note that it could be a pretty big file if you dump your whole Salesforce org.  _(Probably not gigabytes, but certainly many megabytes.)_

_(You can call it something besides `schema.json` by editing the value of the `cumulusci.yml` file's `tasks.get_schema_details.options.filename` property before you run the `cci task run` command.)_

If you run this script multiple times in a row, it will overwrite any old `schema.json` files, so if you needed something, back it up to elsewhere on your hard drive before running this script again.

---

## Use cases

* [blackhat-hemsworth](https://github.com/blackhat-hemsworth) built a [Python script that postprocesses `schema.json`](https://github.com/blackhat-hemsworth/Salesforce-to-Data-Cookbook) into a CSV file acceptable to [iData](https://www.idatainc.com/)'s [Data Cookbook](https://www.datacookbook.com/) cloud-based [data dictionary](https://en.wikipedia.org/wiki/Data_dictionary) product, so that each Salesforce object and field can get its own "Data Model" record in Data Cookbook, with all of the fields tucked tidily into their objects, and all of the lookup relationships and master-detail relationships arranged as Foreign Key cross-references.  From what blackhat-hemsworth tells me, there's even a visual schema browser inside Data Cookbook that's a little easier to use than Salesforce's schema browser.  Nice work.

**Share your wins:**  [Tell me what kinds of cool stuff you do with this data!](https://katiekodes.com/cci-download-schema/)

-[Katie Kodes](https://katiekodes.com/)